import pyglet

window = pyglet.window.Window()
window.push_handlers(pyglet.window.event.WindowEventLogger())

pyglet.app.run()