"""
NeuroNest — Console Interface
Rich terminal UI with status bars, color-coded output, and command system.
"""
import sys
import time

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


class ConsoleInterface:
    """Rich terminal interface for NeuroNest."""

    def __init__(self, engine, evolution, emotions, memory, personality, voice=None):
        self.engine = engine
        self.evolution = evolution
        self.emotions = emotions
        self.memory = memory
        self.personality = personality
        self.voice = voice
        self.running = False
        self.voice_enabled = False

        if HAS_RICH:
            self.console = Console()
        else:
            self.console = None

    def start(self):
        """Start the interactive console session."""
        self.running = True
        self._show_banner()
        self._show_greeting()

        while self.running:
            try:
                user_input = self._get_input()
                if user_input is None:
                    continue
                if user_input.strip() == "":
                    continue

                # Process through the intelligence engine
                result = self.engine.process_input(user_input)

                # Handle commands
                if result.get("raw_command"):
                    self._handle_command(result["raw_command"])
                    continue

                # Display response
                self._display_response(result)

                # Check for exit
                if result.get("should_exit"):
                    self.running = False
                    break

                # Check for evolution
                if result.get("progression_check") and result["progression_check"].get("ready"):
                    self._show_evolution_prompt(result["progression_check"])

            except KeyboardInterrupt:
                self._print_nn("\nOh! Was that an accident? Type 'bye' to say goodbye! 😊")
            except Exception as e:
                self._print_system(f"Error: {e}")

        self._show_farewell_stats()

    def _show_banner(self):
        """Display the NeuroNest startup banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗             ║
║     ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗            ║
║     ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║            ║
║     ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║            ║
║     ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝            ║
║     ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝            ║
║                    N E S T                                    ║
║                                                              ║
║        ✧ Intelligence that evolves, not installs ✧           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝"""

        if self.console:
            self.console.print(banner, style="bold cyan")
            stage = self.evolution.get_current_stage()
            self.console.print(
                f"  Stage {self.evolution.current_stage_id}: "
                f"{stage.get('name', '?')} ({stage.get('age_label', '?')})",
                style="bold yellow"
            )
            self.console.print(
                f"  XP: {self.evolution.total_xp} | "
                f"Interactions: {self.evolution.total_interactions}",
                style="dim"
            )
            self.console.print()
            self.console.print(
                "  Type /help for commands • Type naturally to chat",
                style="dim italic"
            )
            self.console.print("─" * 60, style="dim")
        else:
            print(banner)
            print("  Type /help for commands • Type naturally to chat")
            print("─" * 60)

    def _show_greeting(self):
        """Show initial greeting."""
        stage_id = self.evolution.current_stage_id
        user_name = self.memory.get_user_name()
        greeting = self.personality.get_greeting_style(stage_id, user_name)
        self._print_nn(greeting)

    def _get_input(self):
        """Get user input with styled prompt."""
        try:
            if self.console:
                self.console.print()
                user_input = self.console.input("[bold green]You:[/] ")
            else:
                print()
                user_input = input("You: ")
            return user_input
        except EOFError:
            self.running = False
            return None

    def _display_response(self, result):
        """Display NeuroNest's response with styling."""
        response = result.get("response", "")
        if not response:
            return

        emotion = result.get("emotion", "calm")
        xp = result.get("xp_earned", 0) + result.get("xp_bonus", 0)

        self._print_nn(response)

        # Show XP gain
        if xp > 0 and self.console:
            self.console.print(f"  [dim]+{xp} XP[/]", style="dim yellow")

        # Show milestone
        milestone = result.get("milestone_achieved")
        if milestone:
            if self.console:
                self.console.print(
                    Panel(f"🏆 {milestone}", style="bold gold1", box=box.DOUBLE)
                )
            else:
                print(f"\n🏆 MILESTONE: {milestone}\n")

        # Speak if voice enabled
        if self.voice_enabled and self.voice:
            self.voice.speak(response)

    def _print_nn(self, text):
        """Print NeuroNest's response."""
        emotion_colors = {
            "joy": "bright_yellow",
            "curiosity": "bright_cyan",
            "confusion": "bright_magenta",
            "concern": "bright_red",
            "excitement": "bright_green",
            "calm": "bright_blue",
        }
        emotion = self.emotions.get_dominant_emotion()
        color = emotion_colors.get(emotion, "bright_blue")

        if self.console:
            emoji = self.emotions.get_response_modifier().get("emoji", "🧠")
            self.console.print(
                f"\n[bold {color}]NeuroNest {emoji}:[/] {text}"
            )
        else:
            print(f"\nNeuroNest: {text}")

    def _print_system(self, text):
        """Print system messages."""
        if self.console:
            self.console.print(f"[dim italic]⚙ {text}[/]")
        else:
            print(f"⚙ {text}")

    def _handle_command(self, command_text):
        """Handle slash commands."""
        parts = command_text.strip().split()
        cmd = parts[0].lower().lstrip("/")

        commands = {
            "help": self._cmd_help,
            "status": self._cmd_status,
            "memory": self._cmd_memory,
            "emotions": self._cmd_emotions,
            "milestones": self._cmd_milestones,
            "evolve": self._cmd_evolve,
            "voice": self._cmd_voice,
            "reset": self._cmd_reset,
            "quit": self._cmd_quit,
            "exit": self._cmd_quit,
        }

        handler = commands.get(cmd)
        if handler:
            handler()
        else:
            self._print_system(f"Unknown command: /{cmd}. Type /help for available commands.")

    def _cmd_help(self):
        """Show help."""
        if self.console:
            table = Table(title="🧠 NeuroNest Commands", box=box.ROUNDED)
            table.add_column("Command", style="bold cyan")
            table.add_column("Description", style="white")
            table.add_row("/status", "Show evolution status, XP, and stage info")
            table.add_row("/memory", "View memory statistics")
            table.add_row("/emotions", "View current emotional state")
            table.add_row("/milestones", "View milestone progress")
            table.add_row("/evolve", "Attempt to evolve to next stage")
            table.add_row("/voice", "Toggle voice output on/off")
            table.add_row("/reset", "Reset NeuroNest (careful!)")
            table.add_row("/help", "Show this help menu")
            table.add_row("/quit", "Exit NeuroNest")
            self.console.print(table)
        else:
            print("\nCommands: /status /memory /emotions /milestones /evolve /voice /reset /help /quit")

    def _cmd_status(self):
        """Show evolution status."""
        status = self.evolution.get_status()
        xp_bar = self.evolution.get_xp_bar()

        if self.console:
            table = Table(title="📊 Evolution Status", box=box.ROUNDED)
            table.add_column("Property", style="bold cyan")
            table.add_column("Value", style="white")
            table.add_row("Stage", f"{status['stage_id']}: {status['stage_name']}")
            table.add_row("Age", status['age_label'])
            table.add_row("XP Progress", xp_bar)
            table.add_row("Total Interactions", str(status['total_interactions']))
            table.add_row("Age (days)", str(status['age_days']))
            table.add_row("Features", ", ".join(status['unlocked_features'][:5]) + "...")
            self.console.print(table)
        else:
            print(f"\n--- Status ---")
            print(f"Stage: {status['stage_id']} ({status['stage_name']})")
            print(f"XP: {xp_bar}")
            print(f"Interactions: {status['total_interactions']}")

    def _cmd_memory(self):
        """Show memory stats."""
        stats = self.memory.get_stats()
        if self.console:
            table = Table(title="💾 Memory Status", box=box.ROUNDED)
            table.add_column("Category", style="bold cyan")
            table.add_column("Count", style="white")
            table.add_row("Facts stored", str(stats.get('total_facts', 0)))
            table.add_row("Experiences", str(stats.get('total_experiences', 0)))
            table.add_row("Knowledge topics", str(stats.get('total_knowledge_topics', 0)))
            table.add_row("Entities tracked", str(stats.get('total_entities', 0)))
            table.add_row("User name", stats.get('user_name') or "Unknown")
            table.add_row("Session exchanges", str(stats['session']['total_exchanges']))
            self.console.print(table)
        else:
            print(f"\n--- Memory ---")
            for k, v in stats.items():
                if k != "session":
                    print(f"  {k}: {v}")

    def _cmd_emotions(self):
        """Show emotional state."""
        bars = self.emotions.get_emotion_bar()
        dominant = self.emotions.get_dominant_emotion()
        if self.console:
            table = Table(title=f"💚 Emotional State (Dominant: {dominant})", box=box.ROUNDED)
            table.add_column("Emotion", style="bold cyan")
            table.add_column("Level", style="white")
            for emotion, bar in bars.items():
                style = "bold yellow" if emotion == dominant else ""
                table.add_row(emotion.capitalize(), bar, style=style)
            self.console.print(table)
        else:
            print(f"\n--- Emotions (Dominant: {dominant}) ---")
            for emotion, bar in bars.items():
                marker = " ◄" if emotion == dominant else ""
                print(f"  {emotion:12s} {bar}{marker}")

    def _cmd_milestones(self):
        """Show milestone progress."""
        milestones = self.evolution.get_milestone_status()
        if self.console:
            table = Table(title="🏆 Milestones", box=box.ROUNDED)
            table.add_column("Milestone", style="bold cyan")
            table.add_column("Progress", style="white")
            table.add_column("Status", style="white")
            for key, data in milestones.items():
                progress = f"{data['current']}/{data['target']} ({data['percentage']}%)"
                status = "✅ Complete!" if data['completed'] else f"{'█' * (data['percentage'] // 10)}{'░' * (10 - data['percentage'] // 10)}"
                table.add_row(data['label'], progress, status)
            self.console.print(table)
        else:
            print("\n--- Milestones ---")
            for key, data in milestones.items():
                mark = "✅" if data['completed'] else "⬜"
                print(f"  {mark} {data['label']}: {data['current']}/{data['target']}")

    def _cmd_evolve(self):
        """Attempt evolution."""
        success, message = self.evolution.evolve()
        if success:
            if self.console:
                self.console.print(Panel(message, style="bold green", box=box.DOUBLE))
            else:
                print(f"\n*** {message} ***\n")
        else:
            self._print_system(message)

    def _cmd_voice(self):
        """Toggle voice."""
        if self.voice:
            self.voice_enabled = not self.voice_enabled
            state = "ON 🔊" if self.voice_enabled else "OFF 🔇"
            self._print_system(f"Voice output: {state}")
            if self.voice_enabled:
                self.voice.speak("Voice output enabled! Hello!")
        else:
            self._print_system("Voice module not available. Install pyttsx3: pip install pyttsx3")

    def _cmd_reset(self):
        """Reset NeuroNest."""
        if self.console:
            self.console.print("[bold red]⚠ This will reset ALL memory and progress![/]")
            confirm = self.console.input("[bold red]Type 'CONFIRM' to reset: [/]")
        else:
            print("⚠ This will reset ALL memory and progress!")
            confirm = input("Type 'CONFIRM' to reset: ")

        if confirm.strip() == "CONFIRM":
            self.memory.reset_all()
            self.emotions.reset()
            self._print_system("NeuroNest has been reset to initial state.")
        else:
            self._print_system("Reset cancelled.")

    def _cmd_quit(self):
        """Exit NeuroNest."""
        self.memory.consolidate_session()
        self.evolution.increment_milestone("conversations_completed")
        self.running = False

    def _show_evolution_prompt(self, progression):
        """Show evolution ready notification."""
        msg = progression.get("message", "Ready to evolve!")
        if self.console:
            self.console.print(Panel(
                f"🌟 {msg}\nType /evolve to progress!",
                style="bold magenta", box=box.DOUBLE
            ))
        else:
            print(f"\n🌟 {msg}")
            print("Type /evolve to progress!")

    def _show_farewell_stats(self):
        """Show session stats on exit."""
        session = self.memory.short_term.get_session_summary()
        status = self.evolution.get_status()

        if self.console:
            self.console.print("\n")
            table = Table(title="📋 Session Summary", box=box.ROUNDED)
            table.add_column("Stat", style="bold cyan")
            table.add_column("Value", style="white")
            duration = session['duration_seconds']
            mins = int(duration // 60)
            secs = int(duration % 60)
            table.add_row("Duration", f"{mins}m {secs}s")
            table.add_row("Exchanges", str(session['total_exchanges']))
            table.add_row("Facts learned", str(session['facts_learned']))
            table.add_row("Total XP", str(status['total_xp']))
            table.add_row("Topics", ", ".join(session['topics'][:5]) or "General chat")
            self.console.print(table)
            self.console.print("\n[bold cyan]See you next time! 🧠✨[/]\n")
        else:
            print(f"\n--- Session Summary ---")
            print(f"Exchanges: {session['total_exchanges']}")
            print(f"Facts learned: {session['facts_learned']}")
            print(f"Total XP: {status['total_xp']}")
            print("\nSee you next time! 🧠✨\n")
