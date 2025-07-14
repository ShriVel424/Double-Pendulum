import eventlet
eventlet.monkey_patch()


from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import numpy as np
from scipy.integrate import solve_ivp


app = Flask(__name__)
socketio = SocketIO(app)


g = 9.81
L1 = L2 = m1 = m2 = 1.0
state = np.array([np.pi / 2, 0, np.pi / 2, 0])
running = False

def get_pendulum_position(t0: float, tf: float, initial_angles=[-np.pi/6,0]) -> list:
    """Returns a tuple, (time, vals), where vals is a tuple of (x1, x2, y1, y2)
       `t` is the time or x position of the first pendulum"""
   
    #This is for n = 1
    y0 = [initial_angles[0], initial_angles[1], 0, 0] #theta1, theta2, omega1, omega2
    g = 9.81
    L1 = .5
    L2 = .5
    m_1 = 2
    m_2 = 2


    f = lambda t, y: np.array([
        y[2],
        y[3],
        omega_prime_1(y[0], y[1], y[2], y[3]),
        omega_prime_2(y[0], y[1], y[2], y[3])
    ])


    omega_prime_1 = lambda t1, t2, w1, w2: (-g * (2 * m_1 + m_2) * np.sin(t1) - m_2 * g * np.sin(t1 - t2 * 2) - \
        2 * np.sin(t1 - t2) * m_2 * (w2**2 * L2 + w1**2 * L1 * np.cos(t1-t2))) \
        / (L1 * (2 * m_1 + m_2 - m_2 * np.cos(2 * t1 - 2 * t2)))
   
    omega_prime_2 = lambda t1, t2, w1, w2: (2 * np.sin(t1 - t2) * (w1**2 * L1 * (m_1 + m_2)) + g * (m_1 + m_2) * np.cos(t1) \
        + w2**2 * L2 * m_2 * np.cos(t1 - t2)) / (L2 * (2 * m_1 + m_2 - m_2 * np.cos(2 * t1 - 2 * t2)))
   
    sol = solve_ivp(f, (t0, tf), y0, dense_output=True, max_step=0.001)
    solution = sol.y  
    x1_set = L1 * np.sin(solution)[0]
    y1_set = L1 * -np.cos(solution)[0]
    x2_set = x1_set + L2 * np.sin(solution)[1]
    y2_set = y1_set + L2 * np.cos(solution)[1]


    return solution[-1], (x1_set, x2_set, y1_set, y2_set)

def derivatives(state):
   θ1, ω1, θ2, ω2 = state
   delta = θ2 - θ1
   denom1 = (m1 + m2) * L1 - m2 * L1 * np.cos(delta)**2
   denom2 = (L2 / L1) * denom1


   dθ1 = ω1
   dθ2 = ω2


   dω1 = (
       m2 * L1 * ω1**2 * np.sin(delta) * np.cos(delta) +
       m2 * g * np.sin(θ2) * np.cos(delta) +
       m2 * L2 * ω2**2 * np.sin(delta) -
       (m1 + m2) * g * np.sin(θ1)
   ) / denom1


   dω2 = (
       -m2 * L2 * ω2**2 * np.sin(delta) * np.cos(delta) +
       (m1 + m2) * (g * np.sin(θ1) * np.cos(delta) -
                    L1 * ω1**2 * np.sin(delta) -
                    g * np.sin(θ2))
   ) / denom2


   return np.array([dθ1, dω1, dθ2, dω2])


def simulation_loop():
   global running, state
   dt = 0.02


   with app.app_context():
       while running:
           k1 = derivatives(state)
           k2 = derivatives(state + dt * k1 / 2)
           k3 = derivatives(state + dt * k2 / 2)
           k4 = derivatives(state + dt * k3)
           state += dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


           θ1, _, θ2, _ = state
           x1 = L1 * np.sin(θ1)
           y1 = L1 * np.cos(θ1)
           x2 = x1 + L2 * np.sin(θ2)
           y2 = y1 + L2 * np.cos(θ2)


           socketio.emit('pendulum_data', {
               'x1': x1, 'y1': y1,
               'x2': x2, 'y2': y2
           })


           socketio.sleep(dt)


@socketio.on('start')
def start():
   global running, state
   if not running:
       running = True
       state = np.array([np.pi / 2, 0, np.pi / 2, 0])
       socketio.start_background_task(simulation_loop)


@socketio.on('stop')
def stop():
   global running
   running = False


@app.route('/')
def index():
   return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
   return send_from_directory('.', path)


if __name__ == '__main__':
   print("Starting pendulum simulation on http://localhost:5000")
   socketio.run(app, debug=True, port=5000)


app = Flask(__name__)
socketio = SocketIO(app)
running = False


def simulation_loop():
   global running, state
   dt = 0.02



def simulation_loop():
   global running, state
   dt = 0.02


   with app.app_context():
       list_index = 0
       positions = []
       current_multiple = 1
       final_position = [np.pi/6, 0, 0, 0]
       final_position, positions = get_pendulum_position(np.pi/6 * (current_multiple-1), np.pi*6 * current_multiple, initial_angles=final_position)


       while running:
        if (list_index == len(positions)):
            current_multiple+=1
            final_position, positions = get_pendulum_position(np.pi/6 * (current_multiple-1), np.pi*6 * current_multiple, initial_angles=final_position)
            list_index = 0
        x1, x2, y1, y2 = positions[list_index]


        list_index+=1


        socketio.emit('pendulum_data', {
                'x1': x1, 'y1': y1,
               'x2': x2, 'y2': y2
           })


        socketio.sleep(dt)
