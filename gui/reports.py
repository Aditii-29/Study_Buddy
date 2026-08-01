# gui/reports.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ReportsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # Color Palette
        self.bg_card = "#faf6ee"
        self.border_card = "#decfe6"
        self.text_dark = "#4a4e69"
        self.text_purple = "#5e548e"

        # Embedded Main Scrollable Window
        self.scroll_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent", corner_radius=0
        )
        self.scroll_container.pack(fill="both", expand=True)

        # Report Statistics Data
        self.stats = {
            "total_hours": "142h 35m",
            "avg_focus": "88%",
            "total_sessions": "95",
            "longest_session": "3h 40m",
            "longest_date": "On 6 July, 2026",
            "sleep_alerts": "7"
        }

        # ==========================================
        # TOP HEADER BANNER
        # ==========================================
        header_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 15), padx=10)

        lbl_title = ctk.CTkLabel(
            header_frame, text="Study Reports 📖✨",
            font=ctk.CTkFont(family="Comic Sans MS", size=26, weight="bold"),
            text_color=self.text_purple
        )
        lbl_title.pack(side="left")

        lbl_sub = ctk.CTkLabel(
            header_frame, text="Every hour studied tells a story. ♡",
            font=ctk.CTkFont(family="Comic Sans MS", size=13, slant="italic"),
            text_color="#a29bfe"
        )
        lbl_sub.pack(side="left", padx=15, pady=(6, 0))

        # ==========================================
        # 1. TOP STAT CARDS ROW
        # ==========================================
        stats_row = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        stats_row.pack(fill="x", padx=10, pady=(0, 15))

        self.create_stat_card(stats_row, "🕒 Total Hours", self.stats["total_hours"], "All Time", "#9b5de5")
        self.create_stat_card(stats_row, "🎯 Avg Focus", self.stats["avg_focus"], "This Week", "#2a9d8f")
        self.create_stat_card(stats_row, "📖 Sessions", self.stats["total_sessions"], "All Time", "#00b4d8")
        self.create_stat_card(stats_row, "⏳ Longest", self.stats["longest_session"], self.stats["longest_date"], "#ffb703")
        self.create_stat_card(stats_row, "😴 Sleep Alerts", self.stats["sleep_alerts"], "This Week", "#ff7096")

        # ==========================================
        # 2. MIDDLE CHARTS MATRIX ROW
        # ==========================================
        charts_row = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        charts_row.pack(fill="x", padx=10, pady=(0, 15))

        # Chart 1: Weekly Hours
        c1_frame = self.create_card_container(charts_row, "Weekly Study Hours")
        c1_frame.pack(side="left", expand=True, fill="both", padx=5)
        self.embed_line_chart(c1_frame)

        # Chart 2: Subject Distribution
        c2_frame = self.create_card_container(charts_row, "Subject Distribution")
        c2_frame.pack(side="left", expand=True, fill="both", padx=5)
        self.embed_donut_chart(c2_frame)

        # Chart 3: Focus Trend
        c3_frame = self.create_card_container(charts_row, "Focus Trend")
        c3_frame.pack(side="left", expand=True, fill="both", padx=5)
        self.embed_focus_bar_chart(c3_frame)

        # ==========================================
        # 3. LOWER MATRIX ROW
        # ==========================================
        lower_row = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        lower_row.pack(fill="x", padx=10, pady=(0, 15))

        # Sleep Timeline
        sleep_frame = self.create_card_container(lower_row, "🌙 Sleep Incidents Timeline")
        sleep_frame.pack(side="left", expand=True, fill="both", padx=5)
        self.embed_sleep_timeline(sleep_frame)

        # AI Insights Panel
        insights_frame = self.create_card_container(lower_row, "💡 AI Insights")
        insights_frame.configure(width=260)
        insights_frame.pack(side="right", fill="both", padx=5)
        self.render_ai_insights(insights_frame)

        # ==========================================
        # 4. BOTTOM ACTION ROW
        # ==========================================
        bottom_row = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        bottom_row.pack(fill="x", padx=10, pady=(0, 20))

        # Achievements Card
        achieve_card = self.create_card_container(bottom_row, "🏆 Achievements")
        achieve_card.pack(side="left", expand=True, fill="both", padx=5)
        self.render_achievements(achieve_card)

        # Export Report Card
        export_card = self.create_card_container(bottom_row, "📥 Export Report")
        export_card.configure(width=260)
        export_card.pack(side="right", fill="both", padx=5)
        self.render_export_actions(export_card)

    # ==========================================
    # HELPER COMPONENT BUILDERS
    # ==========================================
    def create_card_container(self, parent, title):
        card = ctk.CTkFrame(
            parent, fg_color=self.bg_card, border_width=2,
            border_color=self.border_card, corner_radius=16
        )
        lbl = ctk.CTkLabel(
            card, text=title,
            font=ctk.CTkFont(family="Comic Sans MS", size=12, weight="bold"),
            text_color=self.text_purple
        )
        lbl.pack(anchor="w", padx=12, pady=(8, 4))
        return card

    def create_stat_card(self, parent, title, main_val, sub_val, accent_color):
        card = ctk.CTkFrame(
            parent, fg_color=self.bg_card, border_width=2,
            border_color=self.border_card, corner_radius=14, height=90
        )
        card.pack(side="left", expand=True, fill="both", padx=3)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(family="Comic Sans MS", size=10, weight="bold"),
            text_color=self.text_dark
        ).pack(anchor="w", padx=10, pady=(6, 0))

        ctk.CTkLabel(
            card, text=main_val, font=ctk.CTkFont(family="Comic Sans MS", size=18, weight="bold"),
            text_color=accent_color
        ).pack(anchor="w", padx=10, pady=(1, 0))

        ctk.CTkLabel(
            card, text=sub_val, font=ctk.CTkFont(size=9, slant="italic"),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=10)

    # ==========================================
    # CHART EMBEDDING MATPLOTLIB LOGIC
    # ==========================================
    def embed_line_chart(self, parent):
        fig, ax = plt.subplots(figsize=(2.8, 1.8), facecolor=self.bg_card)
        days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        hours = [3, 5, 3, 2, 3.2, 4.5, 1.8]

        ax.plot(days, hours, marker='o', color='#9b5de5', linewidth=2, markersize=4)
        ax.set_facecolor(self.bg_card)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#4a4e69', labelsize=7)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def embed_donut_chart(self, parent):
        fig, ax = plt.subplots(figsize=(2.8, 1.8), facecolor=self.bg_card)
        sizes = [35, 25, 15, 10, 15]
        colors = ['#9b5de5', '#2a9d8f', '#00b4d8', '#ffb703', '#ff7096']

        ax.pie(sizes, colors=colors, startangle=90, wedgeprops=dict(width=0.4))
        ax.axis('equal')
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def embed_focus_bar_chart(self, parent):
        fig, ax = plt.subplots(figsize=(2.8, 1.8), facecolor=self.bg_card)
        days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        focus = [80, 85, 75, 70, 65, 88, 72]

        ax.bar(days, focus, color='#bda0bc', width=0.5)
        ax.set_facecolor(self.bg_card)
        ax.set_ylim(0, 100)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#4a4e69', labelsize=7)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def embed_sleep_timeline(self, parent):
        fig, ax = plt.subplots(figsize=(3.2, 1.6), facecolor=self.bg_card)
        days = range(1, 15)
        incidents = [0, 0, 1, 0, 0, 2, 0, 3, 0, 0, 2, 0, 0, 1]

        ax.bar(days, incidents, color='#9b5de5', width=0.4)
        ax.set_facecolor(self.bg_card)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(colors='#4a4e69', labelsize=7)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    # ==========================================
    # INSIGHTS & ACTIONS
    # ==========================================
    def render_ai_insights(self, parent):
        insights = [
            "✨ Peak hours: 7 PM - 10 PM.",
            "📈 Focus up 12% this week.",
            "🌙 Late night sleep alerts elevated.",
            "📚 Strongest subject: DSA & Python.",
            "🔥 Streak status: Active!"
        ]
        for item in insights:
            lbl = ctk.CTkLabel(
                parent, text=item, font=ctk.CTkFont(family="Comic Sans MS", size=10),
                text_color=self.text_dark, anchor="w", justify="left"
            )
            lbl.pack(anchor="w", padx=10, pady=2)

    def render_achievements(self, parent):
        badges_frame = ctk.CTkFrame(parent, fg_color="transparent")
        badges_frame.pack(fill="x", padx=5, pady=5)

        badges = [
            ("⭐ 30h", "30h Master"),
            ("🔥 7d", "7d Streak"),
            ("📖 100", "100 Sessions"),
            ("🌙 Owl", "Night Owl"),
            ("🎯 100%", "Pure Focus")
        ]

        for icon, title in badges:
            b_box = ctk.CTkFrame(badges_frame, fg_color="#f0ebf7", corner_radius=10, width=70, height=55)
            b_box.pack(side="left", expand=True, padx=2)
            b_box.pack_propagate(False)

            ctk.CTkLabel(b_box, text=icon, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 1))
            ctk.CTkLabel(b_box, text=title, font=ctk.CTkFont(size=8), text_color=self.text_dark).pack()

    def render_export_actions(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=8)

        btn_pdf = ctk.CTkButton(
            row, text="📄 PDF", width=55, height=28, corner_radius=10,
            fg_color="#ff7096", hover_color="#ff4d6d",
            command=lambda: print("[EXPORT] Generating PDF Report...")
        )
        btn_pdf.pack(side="left", padx=2)

        btn_csv = ctk.CTkButton(
            row, text="📊 CSV", width=55, height=28, corner_radius=10,
            fg_color="#2a9d8f", hover_color="#218377",
            command=lambda: print("[EXPORT] Exporting CSV...")
        )
        btn_csv.pack(side="left", padx=2)

        btn_print = ctk.CTkButton(
            row, text="🖨️ Print", width=55, height=28, corner_radius=10,
            fg_color="#9b5de5", hover_color="#7209b7",
            command=lambda: print("[EXPORT] Opening Print Dialog...")
        )
        btn_print.pack(side="left", padx=2)