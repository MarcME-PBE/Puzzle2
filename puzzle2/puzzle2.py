import threading
from Puzzle1 import Rfid  # Importa la classe des del teu codi existent (puzzle1.py)
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import time

class RC522App:
    def __init__(self):
        # Configuracio de la interficie grafica
        self.window = Gtk.Window(title="Lector RC522")
        self.label = Gtk.Label(label="")
        self.clear_button = Gtk.Button(label="Esborrar")
        self.display_label = Gtk.Label(label="")
        
        self.clear_button.connect("clicked", self.clear_display)

        # Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.pack_start(self.label, False, False, 0)
        vbox.pack_start(self.display_label, False, False, 10)
        vbox.pack_start(self.clear_button, False, False, 0)

        self.window.add(vbox)
        self.window.connect("destroy", Gtk.main_quit)
        self.window.show_all()

        # Inicialitzem el lector RC522
        self.rfid = Rfid()
        self.card_read = False  # Variable per controlar si hi ha una targeta llegida

        # Iniciem el fil per llegir des del lector
        self.run_rfid_thread()

    def clear_display(self, button):
        self.display_label.set_text("Display esborrat!")
        self.display_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))  # Text negre en reiniciar
        self.window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(255, 0, 0, 1))  # Fons vermell
        self.card_read = False  # Reinicialitzar l'estat per poder llegir una nova targeta

	    # Utilitzar GLib.timeout_add per esperar 3 segons (3000 mililisegons) abans de restaurar el format original
        GLib.timeout_add(3000, self.restore_default_format)

    def restore_default_format(self):
	    # Aquesta funcio restaura el text original despres de 3 segons
	    self.display_label.set_text("Aproximi la targeta...")
	    self.display_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))  # Text blanc
	    self.window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 1, 1))  # Fons blau
	    return False  # Retornar False per indicar que el temporitzador nomes ha de correr una vegada
    
    def run_rfid_thread(self):
        # Iniciem el fil per llegir en segon pla
        threading.Thread(target=self.read_rfid, daemon=True).start()

    def read_rfid(self):
        while True:
            if not self.card_read:  # Nomes llegir si no hi ha una targeta ja llegida
                GLib.idle_add(self.update_display_blue)  # Mostrem el fons blau quan esperem la targeta
                uid = self.rfid.read_uid()
                if uid:
                    self.card_read = True  # Marquem que hi ha una targeta present
                    GLib.idle_add(self.update_display_green, uid)  # Actualitzem a verd
                    # Esperem que la targeta es tregui del lector abans de llegir de nou
                    self.wait_until_card_removed()

    def wait_until_card_removed(self):
        """Aquesta funcio espera fins que es retiri la targeta abans de permetre una nova lectura"""
        while self.card_read:
            try:
                id, text = self.rfid.reader.read_no_block()  # No bloqueja el programa si no hi ha targeta
                if not id:  # Si no hi ha targeta, permet una nova lectura
                    print("Targeta retirada, preparat per llegir una nova targeta.")
                    time.sleep(3)
                    self.card_read = False
            except Exception as e:
                print(f"Error: {e}")
                
		
    def update_display_blue(self):
	    """Actualitza el display a blau quan estem esperant la targeta"""
	    self.display_label.set_text("Aproximi la targeta...")
	    self.display_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))  # Text blanc
	    self.window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 1, 1))  # Fons blau
	    
	    return False

    def update_display_green(self, uid_hex):
        """Actualitza el display a verd amb el UID llegit"""
        self.display_label.set_text(f"UID: {uid_hex}")
        self.display_label.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))  # Text negre
        self.window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 1, 0, 1))  # Fons verd
        
        return False

if __name__ == "__main__":
    app = RC522App()
    Gtk.main()
