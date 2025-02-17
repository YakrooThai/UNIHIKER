import tkinter as tk
from tkinter import ttk
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# Default values
BAUDRATE = 9600
PLC_ADDRESS = 1
START_ADDRESS = 40001
MAX_REGISTERS = 10
client = None

def connect_modbus():
    global client
    selected_port = "/dev/ttyACM0"  # . ........... UNIHIKER

    try:
        client = ModbusSerialClient(
            method='rtu',
            port=selected_port,
            baudrate=BAUDRATE,
            timeout=1,
            stopbits=1,
            bytesize=8,
            parity='N'
        )
        if client.connect():
            status_label.config(text="Connected", foreground="green")
            btn_connect.config(state="disabled")
            btn_disconnect.config(state="normal")
            btn_read.config(state="normal")
        else:
            status_label.config(text="Connection failed", foreground="red")
    except Exception as e:
        status_label.config(text=f"Error: {e}", foreground="red")

def disconnect_modbus():
    global client
    if client:
        client.close()
        client = None
    status_label.config(text="Disconnected", foreground="red")
    btn_connect.config(state="normal")
    btn_disconnect.config(state="disabled")
    btn_read.config(state="disabled")

def read_modbus():
    if not client:
        status_label.config(text="Not connected", foreground="red")
        return

    try:
        start_addr = int(write_address_entry.get()) - 40001
        end_addr = int(write_to_entry.get()) - 40001
        num_registers = min(end_addr - start_addr + 1, MAX_REGISTERS)

        if num_registers < 1:
            status_label.config(text="Invalid range", foreground="red")
            return

        response = client.read_holding_registers(start_addr, num_registers, unit=PLC_ADDRESS)
        
        if response.isError():
            status_label.config(text="Read failed", foreground="red")
        else:
            tree.delete(*tree.get_children())
            for i, val in enumerate(response.registers):
                tree.insert("", "end", values=(40001 + start_addr + i, val))
            status_label.config(text="Read successful", foreground="green")
    except ValueError:
        status_label.config(text="Invalid input", foreground="red")
    except ModbusException as e:
        status_label.config(text=f"Modbus Error: {e}", foreground="red")
    except Exception as e:
        status_label.config(text=f"Error: {e}", foreground="red")

def open_keypad(entry_field):
    keypad_window = tk.Toplevel(root)
    keypad_window.title("Keypad")
    keypad_window.geometry("200x250")
    keypad_window.resizable(False, False)

    keypad_input = tk.StringVar()

    def press_key(num):
        keypad_input.set(keypad_input.get() + str(num))

    def clear_key():
        keypad_input.set("")

    def confirm_key():
        entry_field.delete(0, tk.END)
        entry_field.insert(0, keypad_input.get())
        keypad_window.destroy()

    # จัดช่องแสดงค่าตรงกลาง
    keypad_window.columnconfigure(0, weight=1)
    keypad_window.columnconfigure(1, weight=1)
    keypad_window.columnconfigure(2, weight=1)
    keypad_window.rowconfigure(0, weight=1)
    keypad_window.rowconfigure(1, weight=1)
    keypad_window.rowconfigure(2, weight=1)
    keypad_window.rowconfigure(3, weight=1)
    keypad_window.rowconfigure(4, weight=1)

    entry_display = ttk.Entry(keypad_window, textvariable=keypad_input, font=("Arial", 12), width=8, justify="center")
    entry_display.grid(row=0, column=0, columnspan=3, pady=5, padx=5, sticky="nsew")

    buttons = [
        ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
        ('1', 3, 0), ('2', 3, 1), ('3', 3, 2),
        ('0', 4, 1)
    ]
    
    for (text, row, col) in buttons:
        ttk.Button(keypad_window, text=text, command=lambda t=text: press_key(t), width=4).grid(
            row=row, column=col, padx=5, pady=5, sticky="nsew"
        )

    ttk.Button(keypad_window, text="DEL", command=clear_key, width=4).grid(
        row=4, column=0, padx=5, pady=5, sticky="nsew"
    )
    ttk.Button(keypad_window, text="OK", command=confirm_key, width=4).grid(
        row=4, column=2, padx=5, pady=5, sticky="nsew"
    )

root = tk.Tk()
root.title("Yakroo108 Modbus Scanner")
root.geometry("320x480")  # . ................ UNIHIKER

# เพิ่มแถบ 3D สีฟ้า
title_bar = ttk.Label(root, text="YAKROO108 MODBUS POLL", font=("Arial", 12, "bold"), background="blue", foreground="white", relief="raised", anchor="center")
title_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=2, pady=2, ipadx=5, ipady=5)

btn_connect = ttk.Button(root, text="Connect", command=connect_modbus)
btn_connect.grid(row=1, column=0, padx=5, pady=5)

btn_disconnect = ttk.Button(root, text="Disconnect", command=disconnect_modbus, state="disabled")
btn_disconnect.grid(row=1, column=1, padx=5, pady=5)

btn_read = ttk.Button(root, text="Read", command=read_modbus, state="disabled")
btn_read.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

write_frame = ttk.Frame(root)
write_frame.grid(row=3, column=0, columnspan=2, pady=5)

ttk.Label(write_frame, text="Addr:", font=("Arial", 10)).grid(row=0, column=0)
write_address_entry = ttk.Entry(write_frame, width=6, font=("Arial", 10))
write_address_entry.grid(row=0, column=1)
write_address_entry.bind("<Button-1>", lambda e: open_keypad(write_address_entry))

ttk.Label(write_frame, text="To:", font=("Arial", 10)).grid(row=0, column=2)
write_to_entry = ttk.Entry(write_frame, width=6, font=("Arial", 10))
write_to_entry.grid(row=0, column=3)
write_to_entry.bind("<Button-1>", lambda e: open_keypad(write_to_entry))

tree_frame = ttk.Frame(root)
tree_frame.grid(row=4, column=0, columnspan=2, pady=5)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
tree = ttk.Treeview(tree_frame, columns=("Address", "Value"), show="headings", height=6, yscrollcommand=scrollbar.set)

tree.heading("Address", text="Addr")
tree.heading("Value", text="Val")
tree.column("Address", width=110, anchor="center", stretch="yes")
tree.column("Value", width=110, anchor="center", stretch="yes")

scrollbar.config(command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)

status_label = ttk.Label(root, text="Disconnected", font=("Arial", 10))
status_label.grid(row=5, column=0, columnspan=2, pady=5)

root.mainloop()
