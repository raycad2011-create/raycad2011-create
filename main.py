import math
import tkinter as tk
from datetime import datetime
from typing import Optional
import traceback

import customtkinter as ctk

from light.config import load_config
from light.core import AssistantCoordinator
from light.state import AssistantState
from light.utils import clean_command


class LightApp(ctk.CTk):
    """Light's GUI. The coordinator owns all routing and AI calls."""

    def __init__(self):
        super().__init__()
        try:
            self.config = load_config()
            self.is_closing = False
            self.message_count = 0
            self.orb_phase = 0
            self.current_state = AssistantState.IDLE
            self.input_active = False
            self.typing_hint_active = False
            self.typing_hint_job: Optional[str] = None
            self.visual_orb = {
                "intensity": 0.3,
                "core_radius": 28,
                "rings": [42, 53, 62],
            }
            self.animation_job: Optional[str] = None

            self._build_window()
            self._build_ui()

            self.core = AssistantCoordinator(
                self.config,
                on_user_message=self._on_user_message,
                on_assistant_message=self._on_assistant_message,
                on_state_change=self._on_state_change,
                on_listening_change=self._on_listening_change,
            )
            self._add_message("Light", "Light online")
            self.core.speak_async("Light online")
            self._animate_orb()
        except Exception as e:
            print(f"Error initializing app: {e}")
            traceback.print_exc()
            raise

    def _build_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Light")
        self.geometry("820x620")
        self.minsize(640, 500)
        self.configure(fg_color="#071017")
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.bind("<Control-space>", self._focus_command_entry)
        self.bind_all("<Control-space>", self._focus_command_entry)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _build_ui(self):
        shell = ctk.CTkFrame(self, fg_color="#071017")
        shell.grid(row=0, column=0, sticky="nsew")
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(shell, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Light",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#e8fbff",
        )
        title.grid(row=0, column=0, sticky="w")

        self.status_label = ctk.CTkLabel(
            header,
            text="Light is ready",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#7bdff2",
        )
        self.status_label.grid(row=0, column=2, sticky="e")

        core = ctk.CTkFrame(shell, fg_color="transparent")
        core.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 10))
        core.grid_columnconfigure(0, weight=1)

        self.orb_canvas = tk.Canvas(
            core,
            width=132,
            height=132,
            bg="#071017",
            bd=0,
            highlightthickness=0,
        )
        self.orb_canvas.grid(row=0, column=0)

        self.core_label = ctk.CTkLabel(
            core,
            text="READY",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#75d8ff",
        )
        self.core_label.grid(row=1, column=0)

        self.chat_frame = ctk.CTkScrollableFrame(
            shell,
            fg_color="#0a151d",
            corner_radius=12,
            border_width=1,
            border_color="#123142",
            scrollbar_button_color="#164559",
            scrollbar_button_hover_color="#1f6b86",
        )
        self.chat_frame.grid(row=2, column=0, sticky="nsew", padx=24, pady=(0, 14))
        self.chat_frame.grid_columnconfigure(0, weight=1)

        controls = ctk.CTkFrame(shell, fg_color="#09141c", corner_radius=12, border_width=1, border_color="#123142")
        controls.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 20))
        controls.grid_columnconfigure(0, weight=1)

        self.command_entry = ctk.CTkEntry(
            controls,
            placeholder_text="Ask Light...",
            height=44,
            corner_radius=10,
            border_color="#1d6076",
            fg_color="#0d1c25",
            text_color="#e8fbff",
            placeholder_text_color="#5f7f8c",
        )
        self.command_entry.grid(row=0, column=0, sticky="ew", padx=(12, 8), pady=12)
        self.command_entry.bind("<Return>", self._submit_typed_command)
        self.command_entry.bind("<FocusIn>", self._on_input_focus)
        self.command_entry.bind("<FocusOut>", self._on_input_blur)
        self.command_entry.bind("<KeyRelease>", self._on_input_key)

        self.listen_button = ctk.CTkButton(
            controls,
            text="Start Listening",
            width=136,
            height=44,
            corner_radius=10,
            fg_color="#124a61",
            hover_color="#17627d",
            command=self.toggle_listening,
        )
        self.listen_button.grid(row=0, column=1, padx=(0, 8), pady=12)

        self.speak_button = ctk.CTkButton(
            controls,
            text="Speak",
            width=92,
            height=44,
            corner_radius=10,
            fg_color="#14566f",
            hover_color="#1b7594",
            command=self.start_push_to_talk,
        )
        self.speak_button.grid(row=0, column=2, padx=(0, 8), pady=12)

        self.send_button = ctk.CTkButton(
            controls,
            text="Send",
            width=84,
            height=44,
            corner_radius=10,
            fg_color="#1e7ea0",
            hover_color="#2b9ec4",
            command=self._submit_typed_command,
        )
        self.send_button.grid(row=0, column=3, padx=(0, 12), pady=12)

        self.after(100, self.command_entry.focus_set)

    def _submit_typed_command(self, event=None):
        command = clean_command(self.command_entry.get())
        self.command_entry.delete(0, tk.END)
        if command:
            self.core.submit(command, source="text")
        return "break" if event else None

    def toggle_listening(self):
        if self.core.is_listening():
            self.core.stop_listening()
        else:
            self.core.start_listening()

    def start_push_to_talk(self):
        self.core.start_push_to_talk()

    def _on_user_message(self, text):
        self.after(0, lambda: self._add_message("You", text))

    def _on_assistant_message(self, text):
        def update():
            self._add_message("Light", text)
            if text == "Light offline.":
                self.after(500, self.close_app)

        self.after(0, update)

    def _on_state_change(self, state, label):
        def update():
            self.current_state = state
            status = "Light is ready" if state == AssistantState.IDLE else label
            self.status_label.configure(text=status)
            self._set_core_label(state)
            self._set_controls_enabled(state != AssistantState.THINKING)

        self.after(0, update)

    def _on_listening_change(self, listening):
        self.after(
            0,
            lambda: self.listen_button.configure(text="Stop Listening" if listening else "Start Listening"),
        )

    def _focus_command_entry(self, event=None):
        if self.is_closing:
            return "break"
        self.command_entry.focus_set()
        self.command_entry.configure(border_color="#7bdff2")
        self.status_label.configure(text="Ready when you are")
        return "break"

    def _on_input_focus(self, event=None):
        self.input_active = True
        self.command_entry.configure(border_color="#7bdff2")

    def _on_input_blur(self, event=None):
        self.input_active = False
        if self.current_state == AssistantState.IDLE:
            self.command_entry.configure(border_color="#1d6076")

    def _on_input_key(self, event=None):
        if not event or event.keysym in {"Return", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R"}:
            return
        self.typing_hint_active = bool(self.command_entry.get().strip())
        if self.typing_hint_job:
            self.after_cancel(self.typing_hint_job)
        self.typing_hint_job = self.after(900, self._clear_typing_hint)

    def _clear_typing_hint(self):
        self.typing_hint_active = False
        self.typing_hint_job = None

    def _set_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.command_entry.configure(state=state)
        self.send_button.configure(state=state)

    def _set_core_label(self, state):
        labels = {
            AssistantState.IDLE: "READY",
            AssistantState.LISTENING: "LISTENING",
            AssistantState.THINKING: "THINKING",
            AssistantState.SPEAKING: "SPEAKING",
            AssistantState.PAUSED: "PAUSED",
            AssistantState.ERROR: "READY",
        }
        self.core_label.configure(text=labels.get(state, "READY"), text_color=self._state_color(state))

    def _animate_orb(self):
        if self.is_closing:
            return

        self.orb_phase += 1
        pulse = (math.sin(self.orb_phase / 7.0) + 1) / 2
        settings = self._orb_settings(self.current_state, pulse)
        self._blend_orb(settings)

        canvas = self.orb_canvas
        canvas.delete("all")
        center = 66
        for index, radius in enumerate(self.visual_orb["rings"]):
            alpha = max(0.18, self.visual_orb["intensity"] - (index * 0.14))
            color = self._scaled_color(settings["color"], alpha)
            canvas.create_oval(center - radius, center - radius, center + radius, center + radius, outline=color, width=max(1, 4 - index))

        core_radius = self.visual_orb["core_radius"]
        canvas.create_oval(
            center - core_radius,
            center - core_radius,
            center + core_radius,
            center + core_radius,
            fill=self._scaled_color(settings["color"], min(1.0, self.visual_orb["intensity"] + 0.2)),
            outline="#d8f8ff",
            width=1,
        )
        canvas.create_oval(center - 17, center - 17, center + 17, center + 17, fill="#e8fbff", outline="")
        canvas.create_text(center, center, text="L", fill="#071017", font=("Segoe UI", 16, "bold"))
        self.animation_job = self.after(70, self._animate_orb)

    def _orb_settings(self, state, pulse):
        if state == AssistantState.LISTENING:
            return {"color": "#58d7ff", "intensity": 0.45 + pulse * 0.42, "core_radius": 30 + pulse * 5, "rings": (39 + pulse * 4, 51 + pulse * 7, 62 + pulse * 9)}
        if state == AssistantState.THINKING:
            return {"color": "#9bb8ff", "intensity": 0.36 + pulse * 0.28, "core_radius": 29 + pulse * 3, "rings": (39 + pulse * 2, 50 + pulse * 5, 61 + pulse * 7)}
        if state == AssistantState.SPEAKING:
            return {"color": "#7df7d4", "intensity": 0.55 + pulse * 0.38, "core_radius": 32 + pulse * 5, "rings": (41 + pulse * 4, 53 + pulse * 7, 64 + pulse * 8)}
        return {"color": "#3b9fbd", "intensity": 0.3 + pulse * 0.18, "core_radius": 28 + pulse * 2, "rings": (39 + pulse * 2, 50 + pulse * 3, 60 + pulse * 4)}

    def _blend_orb(self, target):
        blend = 0.16
        self.visual_orb["intensity"] = self._lerp(self.visual_orb["intensity"], target["intensity"], blend)
        self.visual_orb["core_radius"] = self._lerp(self.visual_orb["core_radius"], target["core_radius"], blend)
        for index, radius in enumerate(target["rings"]):
            self.visual_orb["rings"][index] = self._lerp(self.visual_orb["rings"][index], radius, blend)

    def _lerp(self, current, target, amount):
        return current + (target - current) * amount

    def _state_color(self, state):
        colors = {
            AssistantState.IDLE: "#6fb8cf",
            AssistantState.LISTENING: "#58d7ff",
            AssistantState.THINKING: "#9bb8ff",
            AssistantState.SPEAKING: "#7df7d4",
            AssistantState.PAUSED: "#8095a0",
            AssistantState.ERROR: "#6fb8cf",
        }
        return colors.get(state, "#75d8ff")

    def _scaled_color(self, color, intensity):
        intensity = max(0.0, min(1.0, intensity))
        color = color.lstrip("#")
        red = int(int(color[0:2], 16) * intensity)
        green = int(int(color[2:4], 16) * intensity)
        blue = int(int(color[4:6], 16) * intensity)
        return f"#{red:02x}{green:02x}{blue:02x}"

    def _add_message(self, sender, message):
        if self.is_closing or not message:
            return

        is_user = sender.lower() == "you"
        row = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        row.grid(row=self.message_count, column=0, sticky="ew", padx=12, pady=(8, 4))
        row.grid_columnconfigure(0, weight=1)

        timestamp = datetime.now().strftime("%I:%M %p").lstrip("0")
        meta = ctk.CTkLabel(row, text=f"{sender} - {timestamp}", font=ctk.CTkFont(size=11), text_color="#5d7985")
        meta.grid(row=0, column=0, sticky="e" if is_user else "w", padx=8)

        bubble_color = "#12384a" if is_user else "#0e2532"
        border_color = "#2b9ec4" if is_user else "#1c5368"
        text_color = "#f2fbff" if is_user else "#d9f7ff"
        bubble = ctk.CTkFrame(row, fg_color=bubble_color, corner_radius=12, border_width=1, border_color=border_color)
        bubble.grid(row=1, column=0, sticky="e" if is_user else "w", padx=4, pady=(2, 0))

        width = max(280, min(560, int(self.winfo_width() * 0.62)))
        text_box = ctk.CTkTextbox(
            bubble,
            font=ctk.CTkFont(size=14),
            text_color=text_color,
            fg_color=bubble_color,
            border_width=0,
            width=width,
            height=self._message_height(message, width),
            wrap="word",
            activate_scrollbars=False,
        )
        text_box.grid(row=0, column=0, padx=12, pady=9, sticky="w")
        text_box.insert("1.0", message)
        text_box.configure(state="disabled")
        text_box.bind("<Button-3>", lambda event, widget=text_box: self._copy_selected_text(widget))
        text_box.bind("<Control-c>", lambda event, widget=text_box: self._copy_selected_text(widget))

        self.message_count += 1
        self._scroll_chat_to_bottom()

    def _message_height(self, message, width):
        characters_per_line = max(28, width // 8)
        visual_lines = 0
        for line in message.splitlines() or [""]:
            visual_lines += max(1, (len(line) // characters_per_line) + 1)
        return max(42, min(220, visual_lines * 22 + 18))

    def _copy_selected_text(self, widget):
        try:
            selected = widget.get("sel.first", "sel.last")
        except tk.TclError:
            return "break"
        if selected:
            self.clipboard_clear()
            self.clipboard_append(selected)
        return "break"

    def _scroll_chat_to_bottom(self):
        def scroll():
            canvas = getattr(self.chat_frame, "_parent_canvas", None)
            if canvas and not self.is_closing:
                canvas.yview_moveto(1.0)
        self.after(20, scroll)

    def close_app(self):
        if self.is_closing:
            return
        self.is_closing = True
        
        # Cancel pending callbacks
        if self.typing_hint_job:
            self.after_cancel(self.typing_hint_job)
        if self.animation_job:
            self.after_cancel(self.animation_job)
        
        try:
            self.core.close()
        except Exception as e:
            print(f"Error closing core: {e}")
        self.destroy()


def main():
    app = LightApp()
    app.mainloop()


if __name__ == "__main__":
    main()
