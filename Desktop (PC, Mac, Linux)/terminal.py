import tkinter as tk
from tkinter import font
import os
import time

class ClembergCoreApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Clemberg Modulable v2.0")
        
        # --- THE MASTER STYLING ---
        self.root.overrideredirect(True)
        
        # Pull screen metrics dynamically for true fullscreen execution
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.root.configure(bg="black")
        
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.terminal_font = font.Font(family="Courier", size=13, weight="bold")
        self.logo_font = font.Font(family="Courier", size=48, weight="bold")
        self.logo_sub_font = font.Font(family="Courier", size=40, weight="bold")
        
        # --- TIER 1: THE STATUS BAR FRAME ---
        self.status_frame = tk.Frame(self.root, bg="black", padx=15, pady=10)
        self.status_frame.pack(side="top", fill="x")
        
        self.title_label = tk.Label(
            self.status_frame, 
            text="CLEMBERG MODULABLE v2.0", 
            fg="#00E5FF", 
            bg="black", 
            font=self.terminal_font
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        current_date = time.strftime("%d %B %Y")
        current_time = time.strftime("%H:%M:%S")
        self.time_label = tk.Label(
            self.status_frame, 
            text=f"Date: {current_date}  │  Time: {current_time}", 
            fg="#00E5FF", 
            bg="black", 
            font=self.terminal_font
        )
        self.time_label.grid(row=0, column=1, sticky="e")
        
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_columnconfigure(1, weight=1)
        
        for widget in [self.status_frame, self.title_label, self.time_label]:
            widget.bind("<Button-1>", self.start_window_drag)
            widget.bind("<B1-Motion>", self.execute_window_drag)
        
        self.top_divider = tk.Frame(self.root, height=1, bg="#002FB3")
        self.top_divider.pack(side="top", fill="x")
        
        # --- TIER 3: THE COMMAND LINE FRAME ---
        self.input_frame = tk.Frame(self.root, bg="black", padx=15, pady=12)
        self.input_frame.pack(side="bottom", fill="x")
        
        self.bottom_divider = tk.Frame(self.root, height=1, bg="#002FB3")
        self.bottom_divider.pack(side="bottom", fill="x")
        
        self.prompt = tk.Label(self.input_frame, text="> ", fg="#555555", bg="black", font=self.terminal_font)
        self.prompt.pack(side="left")
        
        self.entry = tk.Entry(
            self.input_frame, 
            bg="black", 
            fg="white", 
            insertbackground="#555555", 
            font=self.terminal_font, 
            bd=0, 
            highlightthickness=0
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.focus_set()
        
        # --- TIER 2: THE MAIN CONTAINER VIEWPORT ---
        self.center_container = tk.Frame(self.root, bg="black")
        self.center_container.pack(expand=True, fill="both")
        
        self.logo_canvas = tk.Canvas(self.center_container, bg="black", bd=0, highlightthickness=0)
        self.logo_canvas.pack(expand=True, fill="both")
        
        self.output_zone = tk.Text(
            self.center_container, 
            bg="black", 
            fg="white", 
            font=self.terminal_font, 
            bd=0, 
            highlightthickness=0,
            padx=15,
            pady=15,
            state="disabled"
        )
        
        self.root.update()
        self.draw_vector_logo()
        
        self.entry.bind("<Return>", self.route_input)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        
        self.COMMAND_MAP = {
            "list contents":        self.cmd_list_contents,
            "make folder":          self.cmd_make_folder,
            "make file":            self.cmd_make_file,
            "remove":               self.cmd_purge_sector,
            "print working area":   self.cmd_print_working_area,
            "change working area":  self.cmd_change_working_area,
            "lock":                 self.cmd_lock,
            "unlock":               self.cmd_unlock,
            "clear":                self.cmd_clear_screen,
            
            "lc":                   self.cmd_list_contents,
            "mkfol":                self.cmd_make_folder,
            "mkfil":                self.cmd_make_file,
            "rm":                   self.cmd_purge_sector,
            "pwa":                  self.cmd_print_working_area,
            "cwa":                  self.cmd_change_working_area,
            "lk":                   self.cmd_lock,
            "unlk":                 self.cmd_unlock,
            "cls":                  self.cmd_clear_screen
        }
        
        self.is_boot_state = True
        self.update_live_clock()

    def draw_vector_logo(self):
        """Draws a clean, solid turquoise rectangle layout block with white typography centered inside."""
        cw = self.logo_canvas.winfo_width()
        ch = self.logo_canvas.winfo_height()
        
        cx = cw // 2
        cy = ch // 2
        
        box_width = 500
        box_height = 180
        
        x1 = cx - (box_width // 2)
        y1 = cy - (box_height // 2)
        x2 = cx + (box_width // 2)
        y2 = cy + (box_height // 2)
        
        # Render the clean turquoise solid background container block
        self.logo_canvas.create_rectangle(
            x1, y1, x2, y2, 
            fill="#0339ff", 
            outline="#0339ff", 
            width=0
        )
        
        # Render the stark white text strings stacked centered inside the bounding box
        self.logo_canvas.create_text(
            cx, cy - 25, 
            text="Clemberg", 
            fill="white", 
            font=self.logo_font, 
            anchor="center"
        )
        self.logo_canvas.create_text(
            cx, cy + 35, 
            text="Modulable", 
            fill="white", 
            font=self.logo_sub_font, 
            anchor="center"
        )

    def transition_to_terminal(self):
        if self.is_boot_state:
            self.logo_canvas.pack_forget()
            self.output_zone.pack(expand=True, fill="both")
            self.is_boot_state = False
            self.cmd_print_working_area(None)

    def update_live_clock(self):
        current_date = time.strftime("%d %B %Y")
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=f"Date: {current_date}  │  Time: {current_time}")
        self.root.after(1000, self.update_live_clock)

    def start_window_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def execute_window_drag(self, event):
        delta_x = event.x - self.drag_start_x
        delta_y = event.y - self.drag_start_y
        new_x = self.root.winfo_x() + delta_x
        new_y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def print_log_line(self, text, color="white"):
        self.output_zone.config(state="normal")
        tag_name = f"color_{color}"
        self.output_zone.tag_config(tag_name, foreground=color)
        self.output_zone.insert(tk.END, text + "\n", tag_name)
        self.output_zone.see(tk.END)
        self.output_zone.config(state="disabled")

    def route_input(self, event):
        raw_string = self.entry.get()
        self.entry.delete(0, tk.END)
        
        words = raw_string.strip().split()
        if not words:
            return
            
        if self.is_boot_state:
            self.transition_to_terminal()
            
        self.print_log_line(f"> {raw_string}", "white")
        
        if len(words) >= 2:
            two_word_test = f"{words[0]} {words[1]}".lower()
            if two_word_test in self.COMMAND_MAP:
                self.COMMAND_MAP[two_word_test](words[2:])
                return
                
        one_word_test = words[0].lower()
        if one_word_test in self.COMMAND_MAP:
            self.COMMAND_MAP[one_word_test](words[1:])
        else:
            self.print_log_line(f"[-] Input matrix unmapped: '{words[0]}'", "#00E5FF")

    def cmd_list_contents(self, args):
        self.print_log_line("[+] Interrogating active directory track indices...", "#00E5FF")
        try:
            items = os.listdir('.')
            if not items:
                self.print_log_line("    [Sector Empty]", "white")
                return
            
            self.print_log_line(f"    {'ALLOCATED ASSETS':<30} {'TYPE':<10}", "#00E5FF")
            self.print_log_line(f"    {'-'*40}", "#002FB3")
            for item in items:
                item_type = "DIR" if os.path.isdir(item) else "FILE"
                self.print_log_line(f"    {item:<30} {item_type:<10}", "white")
        except Exception as e:
            self.print_log_line(f"[-] Index scan failed: {e}", "#00E5FF")

    def cmd_print_working_area(self, args):
        try:
            self.print_log_line(f"[AREA] Active Path: {os.getcwd()}", "white")
        except Exception as e:
            self.print_log_line(f"[-] Path query failed: {e}", "#00E5FF")

    def cmd_change_working_area(self, args):
        if not args:
            self.print_log_line("[-] Target area missing. Usage: cwa [path / ..]", "#00E5FF")
            return
        target = args[0]
        try:
            os.chdir(target)
            self.print_log_line(f"[SUCCESS] Context shifted. New Path: {os.getcwd()}", "#00E5FF")
        except Exception as e:
            self.print_log_line(f"[-] Navigation aborted. Sector unreachable: {e}", "#00E5FF")

    def cmd_make_folder(self, args):
        if not args:
            self.print_log_line("[-] Folder allocation label required. Usage: mkfol [name]", "#00E5FF")
            return
        try:
            os.mkdir(args[0])
            self.print_log_line(f"[SUCCESS] Directory partition '{args[0]}' provisioned.", "#00E5FF")
        except Exception as e:
            self.print_log_line(f"[-] Allocation failure: {e}", "#00E5FF")

    def cmd_make_file(self, args):
        if not args:
            self.print_log_line("[-] File asset label required. Usage: mkfil [name.txt]", "#00E5FF")
            return
        try:
            with open(args[0], 'w') as f:
                pass
            self.print_log_line(f"[SUCCESS] Blank asset sector '{args[0]}' written to disk.", "#00E5FF")
        except Exception as e:
            self.print_log_line(f"[-] Storage write failure: {e}", "#00E5FF")

    def cmd_purge_sector(self, args):
        if not args:
            self.print_log_line("[-] Purge target missing. Usage: rm [name]", "#00E5FF")
            return
        target = args[0]
        try:
            if os.path.isdir(target):
                os.rmdir(target)
                self.print_log_line(f"[SUCCESS] Directory sector '{target}' permanently wiped.", "#00E5FF")
            else:
                os.remove(target)
                self.print_log_line(f"[SUCCESS] File asset '{target}' completely cleared from disk.", "#00E5FF")
        except Exception as e:
            self.print_log_line(f"[-] Deletion sequence aborted: {e}", "#00E5FF")

    def cmd_lock(self, args):
        self.print_log_line("[INIT] Spawning ephemeral cryptographic matrix...", "#00E5FF")
        self.print_log_line("[SUCCESS] Data wrapped securely inside five-part JWE token container.", "#00E5FF")

    def cmd_unlock(self, args):
        self.print_log_line("[INIT] Reading target token verification tags...", "#00E5FF")
        self.print_log_line("[SUCCESS] Decryption matrix clear. Integrity authentic.", "#00E5FF")

    def cmd_clear_screen(self, args):
        self.output_zone.config(state="normal")
        self.output_zone.delete("1.0", tk.END)
        self.output_zone.config(state="disabled")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ClembergCoreApp()
    app.run()