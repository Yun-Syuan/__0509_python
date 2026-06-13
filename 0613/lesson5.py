from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

import pandas as pd


class ScoreDistributionApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("成績分數分佈分析器")
		self.root.geometry("1040x640")
		self.root.configure(bg="#eef2ff")

		self.subject_columns = ["語文", "數學", "英語", "物理", "化學"]
		self.analysis_subjects = ["全科總分"] + self.subject_columns

		self.df = self._load_data()
		self.selected_subject = tk.StringVar(value=self.analysis_subjects[0])
		self.analysis_info = tk.StringVar(value="請選擇科目查看整體分數分佈")
		self.summary_text = tk.StringVar(value="平均：-  中位數：-  最低：-  最高：-  合格率：-")

		self._build_ui()
		self.on_analysis_changed()

	def _load_data(self) -> pd.DataFrame:
		csv_path = Path(__file__).with_name("考試分數_3年6班.csv")
		try:
			df = pd.read_csv(csv_path)
		except Exception as exc:
			messagebox.showerror("讀取失敗", f"無法讀取資料檔：\n{csv_path}\n\n{exc}")
			raise

		required = ["學生姓名", "語文", "數學", "英語", "物理", "化學"]
		missing = [col for col in required if col not in df.columns]
		if missing:
			messagebox.showerror("欄位錯誤", f"CSV 缺少必要欄位：{', '.join(missing)}")
			raise ValueError("CSV 欄位不完整")

		return df

	def _build_ui(self) -> None:
		header = tk.Frame(self.root, bg="#eef2ff", padx=16, pady=16)
		header.pack(fill=tk.X)

		tk.Label(
			header,
			text="成績分數分佈分析器",
			font=("微軟正黑體", 20, "bold"),
			foreground="#1e293b",
			background="#eef2ff",
		).pack(side=tk.LEFT)

		subtitle = tk.Label(
			header,
			text="整體分布分析 + 分數區間人數統計",
			font=("微軟正黑體", 11),
			fg="#475569",
			bg="#eef2ff",
		)
		subtitle.pack(side=tk.LEFT, padx=(14, 0))

		main_frame = tk.Frame(self.root, bg="#eef2ff", padx=16, pady=8)
		main_frame.pack(fill=tk.BOTH, expand=True)

		control_frame = tk.Frame(main_frame, bg="#eef2ff")
		control_frame.pack(fill=tk.X, pady=(0, 12))

		tk.Label(
			control_frame,
			text="分析科目：",
			font=("微軟正黑體", 12, "bold"),
			background="#eef2ff",
		).pack(side=tk.LEFT)

		self.subject_box = ttk.Combobox(
			control_frame,
			textvariable=self.selected_subject,
			values=self.analysis_subjects,
			state="readonly",
			font=("微軟正黑體", 12),
			width=16,
		)
		self.subject_box.pack(side=tk.LEFT, padx=(8, 16))
		self.subject_box.bind("<<ComboboxSelected>>", lambda _: self.on_analysis_changed())

		tk.Label(
			control_frame,
			textvariable=self.analysis_info,
			font=("微軟正黑體", 11),
			foreground="#334155",
			background="#eef2ff",
		).pack(side=tk.LEFT)

		content_frame = tk.Frame(main_frame, bg="#eef2ff")
		content_frame.pack(fill=tk.BOTH, expand=True)

		summary_panel = tk.LabelFrame(
			content_frame,
			text="整體統計資訊",
			font=("微軟正黑體", 12, "bold"),
			bg="#f8fafc",
			fg="#1f2937",
			padx=12,
			pady=12,
		)
		summary_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.summary_label = tk.Label(
			summary_panel,
			textvariable=self.summary_text,
			font=("微軟正黑體", 11),
			fg="#1e293b",
			bg="#f8fafc",
			anchor="w",
		)
		self.summary_label.pack(fill=tk.X, pady=(0, 12))

		self.analysis_canvas = tk.Canvas(
			summary_panel,
			bg="white",
			highlightthickness=0,
		)
		self.analysis_canvas.pack(fill=tk.BOTH, expand=True)
		self.analysis_canvas.bind("<Configure>", lambda _: self.on_analysis_changed())

		table_panel = tk.LabelFrame(
			content_frame,
			text="分數區間統計",
			font=("微軟正黑體", 12, "bold"),
			bg="#f8fafc",
			fg="#1f2937",
			padx=12,
			pady=12,
		)
		table_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(14, 0))

		self.table = ttk.Treeview(
			table_panel,
			columns=("range", "count"),
			show="headings",
			height=12,
		)
		self.table.heading("range", text="分數區間")
		self.table.heading("count", text="人數")
		self.table.column("range", width=160, anchor="center")
		self.table.column("count", width=120, anchor="center")
		self.table.pack(fill=tk.BOTH, expand=True)

		footer = tk.Frame(self.root, bg="#eef2ff", pady=12)
		footer.pack(fill=tk.X)
		tk.Label(
			footer,
			text="資料來源：0613/考試分數_3年6班.csv",
			font=("微軟正黑體", 10),
			foreground="#94a3b8",
			background="#eef2ff",
		).pack(side=tk.RIGHT)

	def on_analysis_changed(self) -> None:
		subject = self.selected_subject.get().strip()
		if not subject:
			return

		distribution, summary = self._compute_distribution(subject)
		self._refresh_table(distribution)
		self._draw_distribution(subject, distribution)
		self._update_summary(summary, subject)

	def _compute_distribution(self, subject: str):
		if subject == "全科總分":
			scores = self.df[self.subject_columns].sum(axis=1).astype(float)
			bins = [0, 250, 300, 330, 360, 390, 421, 501]
			labels = ["0-249", "250-299", "300-329", "330-359", "360-389", "390-420", "421-500"]
			pass_threshold = 300
		else:
			scores = self.df[subject].astype(float)
			bins = [0, 60, 70, 80, 90, 101]
			labels = ["0-59", "60-69", "70-79", "80-89", "90-100"]
			pass_threshold = 60

		categories = pd.cut(scores, bins=bins, labels=labels, include_lowest=True, right=False)
		counts = categories.value_counts().reindex(labels, fill_value=0)

		summary = {
			"mean": scores.mean(),
			"median": scores.median(),
			"min": scores.min(),
			"max": scores.max(),
			"pass_rate": float((scores >= pass_threshold).mean() * 100),
			"count": len(scores),
		}

		return counts, summary

	def _update_summary(self, summary: dict, subject: str) -> None:
		pass_label = "300" if subject == "全科總分" else "60"
		self.analysis_info.set(f"分析科目：{subject}，共 {summary['count']} 位學生")
		self.summary_text.set(
			f"平均：{summary['mean']:.1f}    中位數：{summary['median']:.1f}    最低：{summary['min']:.0f}    最高：{summary['max']:.0f}    合格({pass_label})：{summary['pass_rate']:.1f}%"
		)

	def _refresh_table(self, distribution: pd.Series) -> None:
		for item in self.table.get_children():
			self.table.delete(item)

		for interval, count in distribution.items():
			self.table.insert("", tk.END, values=(interval, int(count)))

	def _draw_distribution(self, subject: str, distribution: pd.Series) -> None:
		canvas = self.analysis_canvas
		canvas.delete("all")

		width = max(canvas.winfo_width(), 520)
		height = max(canvas.winfo_height(), 320)
		left_padding = 50
		right_padding = 22
		top_padding = 45
		bottom_padding = 60

		plot_width = width - left_padding - right_padding
		plot_height = height - top_padding - bottom_padding
		if plot_width <= 0 or plot_height <= 0:
			return

		x0 = left_padding
		y0 = height - bottom_padding
		x1 = width - right_padding
		y1 = top_padding

		canvas.create_rectangle(0, 0, width, height, fill="#f8fafc", outline="")
		canvas.create_line(x0, y0, x1, y0, width=2, fill="#334155")
		canvas.create_line(x0, y0, x0, y1, width=2, fill="#334155")

		canvas.create_text(width / 2, 24, text=f"{subject} 分數分佈圖", font=("微軟正黑體", 15, "bold"), fill="#0f172a")
		canvas.create_text(width / 2, height - 24, text="分數區間", font=("微軟正黑體", 10), fill="#475569")
		canvas.create_text(18, height / 2, text="人數", angle=90, font=("微軟正黑體", 10), fill="#475569")

		max_count = max(int(v) for v in distribution.values) if distribution.any() else 1
		step = max(1, max_count // 5)
		for tick in range(0, max_count + 1, step):
			y = y0 - (tick / max_count) * plot_height
			canvas.create_line(x0 - 5, y, x0, y, fill="#64748b")
			canvas.create_text(x0 - 28, y, text=str(tick), font=("微軟正黑體", 9), fill="#475569")
			if tick > 0:
				canvas.create_line(x0, y, x1, y, fill="#e2e8f0")

		colors = ["#2563eb", "#22c55e", "#f97316", "#8b5cf6", "#ec4899", "#14b8a6", "#facc15"]
		slots = len(distribution)
		bar_width = plot_width / max(1, slots) * 0.56
	
		for idx, (label, count) in enumerate(distribution.items()):
			cx = x0 + plot_width * (idx + 0.5) / max(1, slots)
			bar_height = (int(count) / max(1, max_count)) * plot_height
			canvas.create_rectangle(
				cx - bar_width / 2,
				y0 - bar_height,
				cx + bar_width / 2,
				y0,
				fill=colors[idx % len(colors)],
				outline="",
			)
			canvas.create_text(cx, y0 - bar_height - 14, text=str(int(count)), font=("微軟正黑體", 10, "bold"), fill="#0f172a")
			canvas.create_text(cx, y0 + 18, text=str(label), font=("微軟正黑體", 10), fill="#475569")


def main() -> None:
	root = tk.Tk()
	app = ScoreDistributionApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
