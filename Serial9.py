""" 
Toto funguje dobre, narobil som sa. 
MiroR jún 2023
Ešte sem chcem predať sledovanie RTS CTS DTR DSR.
Robil som to v Serial8.py
"""

import serial.tools.list_ports
import serial
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

class COMPorts:

    def __init__(self, data: list):
        self.data = data

    @classmethod
    def get_com_ports(cls):
        data = []
        ports = list(serial.tools.list_ports.comports())

        for port_ in ports:
            obj = Object(data=dict({"device": port_.device, "description": port_.description.split("(")[0].strip()}))
            data.append(obj)

        return cls(data=data)

    @staticmethod
    def get_description_by_device(device: str):
        for port_ in COMPorts.get_com_ports().data:
            if port_.device == device:
                return port_.description

    @staticmethod
    def get_device_by_description(description: str):
        for port_ in COMPorts.get_com_ports().data:
            if port_.description == description:
                return port_.device


class Object:
    def __init__(self, data: dict):
        self.data = data
        self.device = data.get("device")
        self.description = data.get("description")
        


if __name__ == "__main__":
    root = tk.Tk()
    root.title("COM Ports")
    
    # Vytvorenie combo boxu pre výber zariadenia
    combo_label = tk.Label(root, text="Select COM Port:")
    combo_label.pack()

    combo_box = ttk.Combobox(root, values=[port.device for port in COMPorts.get_com_ports().data])
    combo_box.pack()

    # Vytvorenie combo boxu pre výber rýchlosti komunikácie
    baud_label = tk.Label(root, text="Select Baud Rate:")
    baud_label.pack()

    baud_combo_box = ttk.Combobox(root, values=["9600", "115200", "38400"])
    baud_combo_box.pack()

    # Funkcia pre vykonanie pripojenia na vybraný port
    def connect():
        try:
            global ser
            selected_port = combo_box.get()
            selected_baud_rate = baud_combo_box.get()
            print("Connecting to:", selected_port)
            print("Baud Rate:", selected_baud_rate)
            # Tu môžete implementovať pripojenie na vybraný port a nastavenie rýchlosti komunikácie
            ser = serial.Serial(selected_port, baudrate=selected_baud_rate, timeout=1)
            ser.bytesize = serial.EIGHTBITS
            ser.parity = serial.PARITY_NONE
            ser.stopbits = serial.STOPBITS_ONE
            status_label.config(text="Connected", fg="green")
            descript_label.config(text="sem načítať port_.description") #pokus o popis description
            send_entry.focus()
            start_reading_thread()  # Spustenie samostatného vlákna pre neustále čítanie z portu
        except serial.SerialException as e:
            status_label.config(text="Connection Error", fg="red")
            print("Serial Exception:", e)



    # Tlačidlo pre odpojenie
    def disconnect():
        global ser
        print("Disconnecting...")
        # Tu môžete implementovať odpojenie zo sériového portu
        if ser.is_open:
            ser.close()
            status_label.config(text="Disconnected", fg="red")

    connect_button = tk.Button(root, text="Connect", command=connect)
    connect_button.pack()            

    status_label = tk.Label(root, text="Disconnected", fg="red")
    status_label.pack()        

    descript_label = tk.Label(root, text="Description", fg="blue")
    descript_label.pack()        

    disconnect_button = tk.Button(root, text="Disconnect", command=disconnect)
    disconnect_button.pack()

    # Vstup pre odosielanie údajov
    send_label = tk.Label(root, text="Send:")
    send_label.pack()

    send_entry = ttk.Entry(root) #input okienko
    send_entry.pack()

    def send_data(): #údaje na serial port
        data = send_entry.get()
        #data +="\r\n" #asi to pridáva samo
        print("Sending data:", data)
        ser.write(data.encode())
        ser.flush()

    def read_data(): #čítanie zo sériového portu
        if ser.is_open:
            data = ser.readline().decode()
            receive_text.insert("end", data)
            ser.flush()

    def start_reading_thread():
        reading_thread = threading.Thread(target=continuous_read)
        reading_thread.daemon = True  # Vlákno sa ukončí spolu so skriptom
        reading_thread.start()

    def continuous_read():
        while True:
            if ser.is_open:
                data = ser.readline().decode()
                #if data:  # Ak dostaneme nejaké údaje
                #print("Read data:",data)
                receive_text.insert("end", data)
                receive_text.see(tk.END)  # Posun na koniec textu

    def center_window(window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")                        
    

    send_button = tk.Button(root, text="Send", command=send_data)
    send_button.pack()

    # Samoskrolujúce okno pre príjem údajov zo sériového portu
    receive_label = tk.Label(root, text="Receive:")
    receive_label.pack()

    receive_text = scrolledtext.ScrolledText(root, width=40, height=10)
    receive_text.pack(fill="both", expand=True) # roztiahne textscroll podľa hlavného panelu

    center_window(root)
    root.mainloop()
