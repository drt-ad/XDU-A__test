import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import threading
import time


class PressureGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("压力测控仿真系统 - 学号:2 姓名:")
        self.root.geometry("600x400")

        self.serial_port = None
        self.is_open = False
        self.read_thread = None
        self.running = False

        self.create_widgets()
        self.refresh_ports()

    def create_widgets(self):                                                                                       
        # 串口选择区域
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)

        tk.Label(frame_top, text="串口:").pack(side=tk.LEFT)

        self.port_combo = ttk.Combobox(frame_top, width=15)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        

        self.refresh_btn = tk.Button(frame_top, text="刷新", command=self.refresh_ports)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        self.open_btn = tk.Button(frame_top, text="打开串口", command=self.toggle_serial)
        self.open_btn.pack(side=tk.LEFT, padx=5)

        # 发送区域
        frame_send = tk.LabelFrame(self.root, text="发送窗口")
        frame_send.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(frame_send, text="学号:").pack(side=tk.LEFT, padx=5)

        vcmd = (self.root.register(self.validate_id), '%P')
        self.send_entry = tk.Entry(frame_send, width=20, validate="key", validatecommand=vcmd)
        self.send_entry.pack(side=tk.LEFT, padx=5)
        self.send_entry.insert(0, "2")
        self.send_entry.bind("<Return>", lambda event: self.send_id())

        self.send_btn = tk.Button(frame_send, text="发送学号", command=self.send_id)
        self.send_btn.pack(side=tk.LEFT, padx=5)

        # 接收区域
        frame_recv = tk.LabelFrame(self.root, text="接收窗口")
        frame_recv.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.recv_text = tk.Text(frame_recv, height=15)
        self.recv_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 状态栏
        self.status_label = tk.Label(self.root, text="状态: 串口未打开", fg="red")
        self.status_label.pack(pady=5)
    def validate_id(self, P):
        """
        验证学号输入
        :param P: 输入的字符串
        :return: True/False
        """
        if P == "" or P.isdigit():
            return True
        return False

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [p.device for p in ports]
        self.port_combo['values'] = port_list
        if port_list:
            self.port_combo.current(0)

    def toggle_serial(self):
        if not self.is_open:
            self.open_serial()
        else:
            self.close_serial()

    def open_serial(self):
        port = self.port_combo.get()
        if not port:
            self.status_label.config(text="状态: 请选择串口", fg="red")
            return

        try:
            self.serial_port = serial.Serial(port, 9600, timeout=0.1)
            self.is_open = True
            self.open_btn.config(text="关闭串口")
            self.status_label.config(text=f"状态: 串口已打开 {port}", fg="green")

            self.running = True
            self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.read_thread.start()

        except Exception as e:
            self.status_label.config(text=f"状态: 打开失败 {e}", fg="red")

    def close_serial(self):
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=1)

        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

        self.is_open = False
        self.open_btn.config(text="打开串口")
        self.status_label.config(text="状态: 串口已关闭", fg="red")

    def send_id(self):
        if not self.is_open:
            self.status_label.config(text="状态: 串口未打开", fg="red")
            return

        student_id = self.send_entry.get().strip()
        if not student_id:
            self.status_label.config(text="状态: 学号不能为空", fg="red")
            return

        try:
            # 发送学号，以换行结尾
            self.serial_port.write((student_id + "\n").encode("utf-8"))
            self.status_label.config(text=f"状态: 已发送学号 {student_id}", fg="green")
        except Exception as e:
            self.status_label.config(text=f"状态: 发送失败 {e}", fg="red")

    def read_serial(self):
        while self.running:
            try:
                if self.serial_port and self.serial_port.is_open:
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.readline().decode("utf-8", errors="ignore").strip()
                        if data:
                            self.recv_text.insert(tk.END, data + "\n")
                            self.recv_text.see(tk.END)
                time.sleep(0.05)
            except Exception as e:
                print("读取串口错误:", e)
                break

    def on_closing(self):
        self.close_serial()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PressureGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()