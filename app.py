import tkinter as tk
import os
import random
from calendar import monthrange
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tkinter import messagebox, ttk
import mysql.connector
from mysql.connector import Error


def _load_dotenv_file():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip()
        if key:
            os.environ.setdefault(key, value.strip())


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


_load_dotenv_file()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": _to_int(os.getenv("DB_PORT", "3306"), 3306),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "db_2djs"),
}

BG = "#F0F0F0"
CARD = "#FFFFFF"
NAVY = "#2C3E50"
NAVY_LIGHT = "#34495E"
ACCENT = "#E74C3C"
TEXT = "#333333"
MUTED = "#7F8C8D"

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LOGIN_BG_PRIMARY = BASE_DIR / "page.png"
LOGIN_BG_CANDIDATES = [
    LOGIN_BG_PRIMARY,
    ASSETS_DIR / "image-70a1678f-621e-48bb-a074-2c60a2bf4b6d.png",
    ASSETS_DIR / "image-7664eb3b-32e8-4830-b6c2-26742b3ffce0.png",
    ASSETS_DIR / "image-541e8322-cdbf-4122-985d-44ea0a8238d4.png",
]

VIEW_DETAILED_SALES = "vw_detailed_sales"
VIEW_INVENTORY_STATUS = "vw_inventory_status"
VIEW_SUPPLIER_SAFETY = "vw_supplier_safety_audit"

STOCKOUT_REASONS = [
    "Spoilage/Expiry",
    "Damage",
    "Waste",
    "Loss/Theft",
    "Transfer",
    "Donation",
    "Sample/Testing",
    "Shrinkage",
    "Returns",
]

VIEW_COLUMN_LABELS = {
    VIEW_DETAILED_SALES: {
        "transaction_id": "Transaction ID",
        "date_sold": "Date Sold",
        "employee_name": "Employee Name",
        "customer_name": "Customer Name",
        "customer_type": "Customer Type",
        "item_name": "Item Name",
        "product_id": "Product ID",
        "qty_sold": "Qty Sold",
        "price_per_unit": "Price per Unit",
        "line_total": "Line Total",
        "sale_total": "Sale Total",
        "payment_type": "Payment Type",
        "balance_impact": "Balance Impact",
    },
    VIEW_INVENTORY_STATUS: {
        "product_id": "Product ID",
        "product_name": "Product Name",
        "brand": "Brand",
        "size": "Size",
        "stock_quantity": "Stock Quantity",
        "unit_price": "Unit Price",
        "reorder_point": "Reorder Point",
        "stock_gap_kg": "Stock Gap (kg)",
        "last_stockin_date": "Last Stock-In Date",
        "last_sale_date": "Last Sale Date",
        "days_since_last_stockin": "Days Since Last Stock-In",
        "availability_status": "Availability Status",
        "status_priority": "Status Priority",
    },
    VIEW_SUPPLIER_SAFETY: {
        "stockin_id": "Stock-In ID",
        "date_received": "Date Received",
        "supplier_name": "Supplier Name",
        "product_name": "Product Name",
        "quantity_kg": "Quantity (kg)",
        "arrival_temp": "Arrival Temp (C)",
        "temp_breach_c": "Temp Breach (C)",
        "safety_status": "Safety Status",
        "action_level": "Action Level",
    },
}

CUSTOMER_NAME_SQL = """
CASE
    WHEN is_business = 1 THEN business_name
    ELSE TRIM(CONCAT_WS(' ', first_name, middle_name, last_name))
END
""".strip()

QUALIFIED_CUSTOMER_NAME_SQL = """
CASE
    WHEN c.is_business = 1 THEN c.business_name
    ELSE TRIM(CONCAT_WS(' ', c.first_name, c.middle_name, c.last_name))
END
""".strip()


def prettify_column_name(view_name: str, column_name: str) -> str:
    label = VIEW_COLUMN_LABELS.get(view_name, {}).get(column_name)
    if label:
        return label
    return column_name.replace("_", " ").title()


def fetch_view_rows(cursor, view_name: str, order_sql: str, limit: int = 250):
    cursor.execute(f"SELECT * FROM {view_name} ORDER BY {order_sql} LIMIT %s", (limit,))
    cols = [d[0] for d in cursor.description] if cursor.description else []
    rows = [tuple(r) for r in cursor.fetchall()]
    return cols, rows


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@contextmanager
def db_cursor(dictionary: bool = False):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=dictionary)
        yield connection, cursor
    except Error:
        if connection:
            connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

class CalendarDatePicker(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.value_var = tk.StringVar()
        self.popup = None
        self.displayed_year = date.today().year
        self.displayed_month = date.today().month
        self.entry = ttk.Entry(self, textvariable=self.value_var, state="readonly")
        self.entry.pack(side="left", fill="x", expand=True)
        ttk.Button(self, text="Pick", width=6, command=self.open_calendar).pack(side="left", padx=(6, 4))
        ttk.Button(self, text="Clear", width=6, command=self.clear).pack(side="left")
    def get(self):
        return self.value_var.get()
    def clear(self):
        self.value_var.set("")
    def set_date(self, value):
        if not value:
            self.clear()
            return
        if isinstance(value, datetime):
            value = value.date()
        if isinstance(value, date):
            self.value_var.set(value.strftime("%Y-%m-%d"))
            self.displayed_year = value.year
            self.displayed_month = value.month
            return
        parsed = datetime.strptime(str(value), "%Y-%m-%d").date()
        self.value_var.set(parsed.strftime("%Y-%m-%d"))
        self.displayed_year = parsed.year
        self.displayed_month = parsed.month
    def open_calendar(self):
        current_value = self.get().strip()
        if current_value:
            selected = datetime.strptime(current_value, "%Y-%m-%d").date()
        else:
            selected = date.today()
        self.displayed_year = selected.year
        self.displayed_month = selected.month
        if self.popup is None or not self.popup.winfo_exists():
            self.popup = tk.Toplevel(self)
            self.popup.title("Select Date")
            self.popup.transient(self.winfo_toplevel())
            self.popup.resizable(False, False)
            self.popup.configure(bg=CARD)
            self.popup.protocol("WM_DELETE_WINDOW", self._close_popup)
        else:
            for child in self.popup.winfo_children():
                child.destroy()
        self._render_popup()
    def _close_popup(self):
        if self.popup is not None and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = None
    def _change_month(self, delta):
        month = self.displayed_month + delta
        year = self.displayed_year
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        self.displayed_year = year
        self.displayed_month = month
        self._render_popup()
    def _choose_day(self, day):
        selected = date(self.displayed_year, self.displayed_month, day)
        self.set_date(selected)
        self._close_popup()
    def _render_popup(self):
        for child in self.popup.winfo_children():
            child.destroy()
        wrapper = ttk.Frame(self.popup, padding=10)
        wrapper.pack(fill="both", expand=True)
        header = ttk.Frame(wrapper)
        header.pack(fill="x")
        ttk.Button(header, text="<", width=3, command=lambda: self._change_month(-1)).pack(side="left")
        ttk.Label(
            header,
            text=f"{datetime(self.displayed_year, self.displayed_month, 1):%B %Y}",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", expand=True)
        ttk.Button(header, text=">", width=3, command=lambda: self._change_month(1)).pack(side="right")
        days_frame = ttk.Frame(wrapper)
        days_frame.pack(fill="both", expand=True, pady=(8, 0))
        weekday_names = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        for col, label in enumerate(weekday_names):
            ttk.Label(days_frame, text=label, anchor="center", width=4).grid(row=0, column=col, padx=1, pady=(0, 4))
        first_weekday, total_days = monthrange(self.displayed_year, self.displayed_month)
        row = 1
        col = first_weekday
        for day_num in range(1, total_days + 1):
            ttk.Button(
                days_frame,
                text=str(day_num),
                width=4,
                command=lambda value=day_num: self._choose_day(value),
            ).grid(row=row, column=col, padx=1, pady=1)
            col += 1
            if col > 6:
                col = 0
                row += 1
class PoultryCrudApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("2DJS")
        self.geometry("1250x760")
        self.configure(bg=BG)
        self.option_add("*Font", ("Segoe UI", 10))
        self.user = None
        self.cart = []
        self.sales_history_window = None
        self.sales_history_tree = None
        self.stockout_tree = None
        self.customer_balance_by_id = {}
        self._configure_styles()
        if not self._check_database_connection():
            return
        self._build_login()

    def _fetch_rows(self, query, params=()):
        with db_cursor(dictionary=True) as (_, cursor):
            cursor.execute(query, params)
            return cursor.fetchall()

    def _clear_tree(self, tree):
        children = tree.get_children()
        if children:
            tree.delete(*children)

    def _populate_tree(self, tree, rows, value_builder):
        self._clear_tree(tree)
        for row in rows:
            tree.insert("", "end", values=value_builder(row))

    def _set_product_stock_label(self, combo_widget, label_var):
        product_id = self._get_product_id_from_combo(combo_widget)
        if not product_id:
            label_var.set("0.00 kg")
            return
        try:
            with db_cursor(dictionary=True) as (_, cursor):
                cursor.execute("SELECT stock_quantity FROM products WHERE product_id = %s", (product_id,))
                row = cursor.fetchone()
            stock_qty = row["stock_quantity"] if row and row["stock_quantity"] is not None else Decimal("0.00")
            label_var.set(f"{stock_qty} kg")
        except Error:
            label_var.set("N/A")

    def _check_database_connection(self):
        try:
            with db_cursor() as (_, cursor):
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Error as err:
            messagebox.showerror(
                "Database Connection Failed",
                (
                    "Unable to connect to MariaDB/MySQL.\n\n"
                    f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}\n"
                    f"User: {DB_CONFIG['user']}\n"
                    f"Database: {DB_CONFIG['database']}\n\n"
                    f"Error: {err}"
                ),
            )
            self.destroy()
            return False
    def _configure_styles(self):
        style = ttk.Style(self)
        # Prefer clam so ttk buttons use the app's foreground/background colors.
        if "clam" in style.theme_names():
            style.theme_use("clam")
        elif "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Card.TFrame", background=CARD)
        style.configure("Nav.TFrame", background=NAVY)
        style.configure("Title.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 18, "bold"))
        style.configure("Muted.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 10))
        style.configure("Field.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 10, "bold"))
        style.configure("Section.TLabelframe", background=CARD)
        style.configure("Section.TLabelframe.Label", background=CARD, foreground=NAVY, font=("Segoe UI", 10, "bold"))
        style.configure("StockHint.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("StockValue.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 10, "bold"))
        style.configure("StatCard.TFrame", background=CARD)
        style.configure("StatLabel.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("StatValue.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 18, "bold"))
        style.configure("StatMeta.TLabel", background=CARD, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD, foreground=TEXT, padding=(12, 8))
        style.map("TNotebook.Tab", background=[("selected", BG), ("active", BG)], foreground=[("selected", NAVY)])
        style.configure(
            "Treeview",
            background=CARD,
            fieldbackground=CARD,
            foreground=TEXT,
            rowheight=28,
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background=BG,
            foreground=NAVY,
            padding=(8, 8),
            relief="flat",
        )
        style.map("Treeview", background=[("selected", NAVY)], foreground=[("selected", "white")])
        style.configure("Primary.TButton", background=NAVY, foreground="white", borderwidth=0, padding=(10, 8), font=("Segoe UI", 9, "bold"))
        style.map(
            "Primary.TButton",
            background=[("active", NAVY_LIGHT), ("pressed", NAVY_LIGHT)],
            foreground=[("active", "white"), ("!disabled", "white")],
        )
        style.configure(
            "LoginPrimary.TButton",
            background=NAVY,
            foreground="white",
            padding=(12, 12),
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "LoginPrimary.TButton",
            background=[("active", NAVY_LIGHT), ("pressed", NAVY_LIGHT)],
            foreground=[("active", "white"), ("!disabled", "white")],
        )
        style.configure(
            "LoginGhost.TButton",
            background=CARD,
            foreground=NAVY,
            padding=(12, 12),
            borderwidth=1,
            relief="solid",
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "LoginGhost.TButton",
            background=[("active", BG)],
            foreground=[("active", NAVY)],
        )
        style.configure(
            "LoginEntry.TEntry",
            fieldbackground=BG,
            borderwidth=0,
            relief="flat",
            foreground=TEXT,
            insertcolor=TEXT,
            padding=(14, 11),
        )
        style.configure("LoginSecondary.TButton", background=CARD, foreground=NAVY, borderwidth=0)
        style.map(
            "LoginSecondary.TButton",
            background=[("active", BG)],
            foreground=[("active", NAVY)],
        )
        style.configure("Danger.TButton", background=ACCENT, foreground="white", borderwidth=0, font=("Segoe UI", 9, "bold"))
        style.map("Danger.TButton", background=[("active", "#C0392B")], foreground=[("active", "white"), ("!disabled", "white")])
        style.configure("SidePrimary.TButton", background="#FFFFFF", foreground=NAVY, borderwidth=0, padding=(12, 10), font=("Segoe UI", 9, "bold"))
        style.map(
            "SidePrimary.TButton",
            background=[("active", "#EEF3F8"), ("pressed", "#E2EBF5")],
            foreground=[("active", NAVY), ("!disabled", NAVY)],
        )
        style.configure("SideDanger.TButton", background="#FFEDEE", foreground="#9E2A2A", borderwidth=0, padding=(12, 10), font=("Segoe UI", 9, "bold"))
        style.map(
            "SideDanger.TButton",
            background=[("active", "#FFE1E3"), ("pressed", "#FFD4D7")],
            foreground=[("active", "#8A1F1F"), ("!disabled", "#9E2A2A")],
        )
        style.configure("Treeview", rowheight=27, fieldbackground="white", background="white")
        style.configure("Treeview.Heading", background=BG, foreground=TEXT, font=("Segoe UI", 9, "bold"))

    def _clear_root(self):
        for child in self.winfo_children():
            child.destroy()

    def _build_login(self):
        self._clear_root()
        self.configure(bg=BG)
        layout = tk.Frame(self, bg=BG)
        layout.pack(fill="both", expand=True)
        left_panel = tk.Frame(layout, bg=NAVY)
        left_panel.pack(side="left", fill="both", expand=True)
        left_panel.pack_propagate(False)
        right_panel = tk.Frame(layout, bg=BG)
        right_panel.pack(side="right", fill="both", expand=True)
        right_panel.pack_propagate(False)
        self._build_login_left_visual(left_panel)
        login_wrap = tk.Frame(right_panel, bg=CARD)
        login_wrap.place(relx=0.5, rely=0.5, anchor="center", width=460, height=600)
        tk.Label(login_wrap, text="STAFF LOGIN", bg=CARD, fg=TEXT, font=("Segoe UI", 34, "bold")).pack(anchor="w")
        tk.Label(
            login_wrap,
            text="Please enter your credentials to access the inventory portal.",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(8, 34))
        tk.Label(login_wrap, text="STAFF ID / USERNAME", bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.username_var = tk.StringVar()
        ttk.Entry(login_wrap, textvariable=self.username_var, style="LoginEntry.TEntry").pack(fill="x", ipady=9, pady=(8, 16))
        top_pass = tk.Frame(login_wrap, bg=CARD)
        top_pass.pack(fill="x")
        tk.Label(top_pass, text="PASSWORD", bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Label(top_pass, text="FORGOT PASSWORD?", bg=CARD, fg=ACCENT, font=("Segoe UI", 8, "bold")).pack(side="right")
        self.password_var = tk.StringVar()
        ttk.Entry(login_wrap, textvariable=self.password_var, show="*", style="LoginEntry.TEntry").pack(fill="x", ipady=9, pady=(8, 24))
        ttk.Button(login_wrap, text="LOGIN  \u2192", style="LoginPrimary.TButton", command=self._login).pack(fill="x", ipady=8, pady=(4, 0))
        center_tag = tk.Frame(login_wrap, bg=CARD)
        center_tag.pack(fill="x", pady=(24, 16))
        tk.Frame(center_tag, bg=BG, height=1).pack(side="left", fill="x", expand=True, padx=(0, 10))
        tk.Label(center_tag, text="MANAGEMENT PORTAL", bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(side="left")
        tk.Frame(center_tag, bg=BG, height=1).pack(side="left", fill="x", expand=True, padx=(10, 0))
        ttk.Button(login_wrap, text="LOGIN AS ADMIN", style="LoginGhost.TButton", command=self._login_as_admin).pack(fill="x", ipady=6)
        tk.Label(login_wrap, text="", bg=CARD).pack(pady=(66, 0))
        tk.Label(login_wrap, text="(c) 2026 2DJS DRESSED CHICKEN INVENTORY.", bg=CARD, fg=MUTED, font=("Segoe UI", 7, "bold")).pack(anchor="center")
        tk.Label(login_wrap, text="INTERNAL USE ONLY", bg=CARD, fg=MUTED, font=("Segoe UI", 7, "bold")).pack(anchor="center")

    def _build_login_left_visual(self, parent):
        canvas = tk.Canvas(parent, bg=NAVY, highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.login_bg_image = None
        for image_path in LOGIN_BG_CANDIDATES:
            if image_path.exists():
                try:
                    self.login_bg_image = tk.PhotoImage(file=str(image_path))
                    break
                except tk.TclError:
                    continue

        def render_left_brand(_event=None):
            canvas.delete("all")
            width = max(canvas.winfo_width(), 1)
            height = max(canvas.winfo_height(), 1)
            if self.login_bg_image is not None:
                canvas.create_image(width // 2, height // 2, image=self.login_bg_image, anchor="center")
                canvas.create_rectangle(0, 0, width, height, fill="#1f2b38", stipple="gray50", outline="")
            center_x = width // 2
            brand_y = int(height * 0.56)
            canvas.create_text(center_x, brand_y, text="2DJS", fill="white", anchor="center", font=("Segoe UI", 62, "bold"))
            canvas.create_text(
                center_x,
                brand_y + 40,
                text="DRESSED CHICKEN INVENTORY",
                fill="#D6DFE7",
                anchor="center",
                font=("Segoe UI", 8, "bold"),
            )

        canvas.bind("<Configure>", render_left_brand)
        render_left_brand()
    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Missing Data", "Enter username and password.")
            return
        try:
            with db_cursor(dictionary=True) as (_, cursor):
                cursor.execute(
                    """
                    SELECT employee_id, name, username, role
                    FROM employees
                    WHERE username = %s AND password = %s
                    """,
                    (username, password),
                )
                self.user = cursor.fetchone()
        except Error as err:
            messagebox.showerror("Database Error", str(err))
            return
        if not self.user:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return
        self._build_main_ui()
    def _login_as_admin(self):
        self.username_var.set("Heinz")
        self.password_var.set("Heinz")
        self._login()
    def _build_main_ui(self):
        self._clear_root()
        main = ttk.Frame(self, style="Card.TFrame")
        main.pack(fill="both", expand=True, padx=16, pady=16)
        side = ttk.Frame(main, style="Nav.TFrame", width=260)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        ttk.Label(side, text="2DJS", background=NAVY, foreground="white", font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=18, pady=(20, 6)
        )
        ttk.Label(side, text=f"Logged In as: {self.user['name']}", background=NAVY, foreground="#E5ECF2").pack(
            anchor="w", padx=18
        )
        ttk.Label(side, text=f"Role: {self.user['role']}", background=NAVY, foreground="#E5ECF2").pack(
            anchor="w", padx=18, pady=(0, 20)
        )
        ttk.Button(side, text="Refresh All Data", style="SidePrimary.TButton", command=self.refresh_all).pack(fill="x", padx=18, pady=6)
        ttk.Button(side, text="Logout", style="SideDanger.TButton", command=self._build_login).pack(fill="x", padx=18, pady=6)
        content = ttk.Frame(main, style="Card.TFrame", padding=18)
        content.pack(side="left", fill="both", expand=True)
        self.tabs = ttk.Notebook(content)
        self.tabs.pack(fill="both", expand=True, pady=(14, 0))
        self.dashboard_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=12)
        self.products_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=12)
        self.employees_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=12)
        self.customers_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=12)
        self.suppliers_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=12)
        self.stockin_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=12)
        self.stockout_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=12)
        self.sales_tab = ttk.Frame(self.tabs, style="Card.TFrame", padding=12)
        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.products_tab, text="Products")
        self.tabs.add(self.employees_tab, text="Employees")
        self.tabs.add(self.customers_tab, text="Customers")
        self.tabs.add(self.suppliers_tab, text="Suppliers")
        self.tabs.add(self.stockin_tab, text="Stock-In")
        self.tabs.add(self.stockout_tab, text="Stock-Out")
        self.tabs.add(self.sales_tab, text="Sales")
        self._build_dashboard_tab()
        self._build_products_tab()
        self._build_employees_tab()
        self._build_customers_tab()
        self._build_suppliers_tab()
        self._build_stockin_tab()
        self._build_stockout_tab()
        self._build_sales_tab()
        self.refresh_all()
    def _build_products_tab(self):
        form = ttk.Frame(self.products_tab, style="Card.TFrame")
        form.pack(fill="x")
        ttk.Label(form, text="Product Name", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Brand", style="Field.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Size", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Unit Price", style="Field.TLabel").grid(row=0, column=3, sticky="w", padx=(10, 0))
        self.p_name = tk.StringVar()
        self.p_brand = tk.StringVar()
        self.p_size = tk.StringVar()
        self.p_price = tk.StringVar()
        self.product_size_options = ["Small", "Medium", "Large", "Regular", "Jumbo"]
        ttk.Entry(form, textvariable=self.p_name).grid(row=1, column=0, sticky="ew", pady=(4, 8))
        ttk.Entry(form, textvariable=self.p_brand).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 8))
        self.p_size_combo = ttk.Combobox(form, textvariable=self.p_size, values=self.product_size_options, state="readonly")
        self.p_size_combo.grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(4, 8))
        self.p_size.set("Regular")
        ttk.Entry(form, textvariable=self.p_price).grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=(4, 8))
        for idx in range(4):
            form.columnconfigure(idx, weight=1)
        ttk.Label(
            self.products_tab,
            text="Use Products for item setup. Use Stock-In and Stock-Out to change inventory after setup.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(6, 10))
        btns = ttk.Frame(self.products_tab, style="Card.TFrame")
        btns.pack(fill="x", pady=(0, 10))
        ttk.Button(btns, text="Add Product", style="Primary.TButton", command=self.add_product).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Update Product", style="Primary.TButton", command=self.update_product).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Delete Product", style="Danger.TButton", command=self.delete_product).pack(side="left")
        ttk.Button(
            btns,
            text="Inventory Status",
            style="Primary.TButton",
            command=lambda: self.open_reporting_view_popup("vw_inventory_status", "Inventory Status Report"),
        ).pack(side="left", padx=(8, 0))
        self.products_tree = self._create_tree(self.products_tab, ("ID", "Name", "Brand", "Size", "Price", "Stock"))
        self.products_tree.pack(fill="both", expand=True)
        self.products_tree.bind("<<TreeviewSelect>>", self.on_product_select)
    def _build_employees_tab(self):
        form = ttk.Frame(self.employees_tab, style="Card.TFrame")
        form.pack(fill="x")
        ttk.Label(form, text="Name", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Username", style="Field.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Password", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Role", style="Field.TLabel").grid(row=0, column=3, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Date Hired", style="Field.TLabel").grid(row=0, column=4, sticky="w", padx=(10, 0))
        self.e_name = tk.StringVar()
        self.e_username = tk.StringVar()
        self.e_password = tk.StringVar()
        self.e_role = ttk.Combobox(form, state="readonly", values=["Admin", "Staff"])
        self.e_role.set("Staff")
        ttk.Entry(form, textvariable=self.e_name).grid(row=1, column=0, sticky="ew", pady=(4, 8))
        ttk.Entry(form, textvariable=self.e_username).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 8))
        ttk.Entry(form, textvariable=self.e_password, show="*").grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(4, 8))
        self.e_role.grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=(4, 8))
        self.e_date_hired = CalendarDatePicker(form)
        self.e_date_hired.grid(row=1, column=4, sticky="ew", padx=(10, 0), pady=(4, 8))
        for idx in range(5):
            form.columnconfigure(idx, weight=1)
        btns = ttk.Frame(self.employees_tab, style="Card.TFrame")
        btns.pack(fill="x", pady=(0, 10))
        ttk.Button(btns, text="Add Employee", style="Primary.TButton", command=self.add_employee).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Update Employee", style="Primary.TButton", command=self.update_employee).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Delete Employee", style="Danger.TButton", command=self.delete_employee).pack(side="left")
        self.employees_tree = self._create_tree(self.employees_tab, ("ID", "Name", "Username", "Role", "Date Hired"))
        self.employees_tree.pack(fill="both", expand=True)
        self.employees_tree.bind("<<TreeviewSelect>>", self.on_employee_select)
    def _build_customers_tab(self):
        form = ttk.Frame(self.customers_tab, style="Card.TFrame")
        form.pack(fill="x")
        self.c_is_business = tk.IntVar(value=0)
        self.c_business_name = tk.StringVar()
        ttk.Label(form, text="First Name", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Middle Name (Optional)", style="Field.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Last Name", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Contact", style="Field.TLabel").grid(row=0, column=3, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Balance", style="Field.TLabel").grid(row=0, column=4, sticky="w", padx=(10, 0))
        self.c_first_name = tk.StringVar()
        self.c_middle_name = tk.StringVar()
        self.c_last_name = tk.StringVar()
        self.c_contact = tk.StringVar()
        self.c_debt = tk.StringVar(value="0.00")
        self.c_first_name_entry = ttk.Entry(form, textvariable=self.c_first_name)
        self.c_middle_name_entry = ttk.Entry(form, textvariable=self.c_middle_name)
        self.c_last_name_entry = ttk.Entry(form, textvariable=self.c_last_name)
        self.c_first_name_entry.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.c_middle_name_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 8))
        self.c_last_name_entry.grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(4, 8))
        ttk.Entry(form, textvariable=self.c_contact).grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=(4, 8))
        ttk.Entry(form, textvariable=self.c_debt).grid(row=1, column=4, sticky="ew", padx=(10, 0), pady=(4, 8))
        self.c_business_check = ttk.Checkbutton(
            form,
            text="Business Name",
            variable=self.c_is_business,
            command=self._toggle_customer_name_mode,
        )
        self.c_business_check.grid(row=2, column=0, sticky="w", pady=(4, 2))
        ttk.Label(form, text="Business Name", style="Field.TLabel").grid(row=2, column=1, sticky="w", padx=(10, 0), pady=(4, 2))
        self.c_business_name_entry = ttk.Entry(form, textvariable=self.c_business_name)
        self.c_business_name_entry.grid(row=3, column=1, columnspan=3, sticky="ew", padx=(10, 0), pady=(4, 8))
        for idx in range(5):
            form.columnconfigure(idx, weight=1)
        self._toggle_customer_name_mode()
        btns = ttk.Frame(self.customers_tab, style="Card.TFrame")
        btns.pack(fill="x", pady=(0, 10))
        ttk.Button(btns, text="Add Customer", style="Primary.TButton", command=self.add_customer).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Update Customer", style="Primary.TButton", command=self.update_customer).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Delete Customer", style="Danger.TButton", command=self.delete_customer).pack(side="left")
        self.customers_tree = self._create_tree(self.customers_tab, ("ID", "Name", "Contact", "Balance"))
        self.customers_tree.pack(fill="both", expand=True)
        self.customers_tree.bind("<<TreeviewSelect>>", self.on_customer_select)
    def _build_suppliers_tab(self):
        form = ttk.Frame(self.suppliers_tab, style="Card.TFrame")
        form.pack(fill="x")
        ttk.Label(form, text="Supplier Name", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Contact", style="Field.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Address", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.sup_name = tk.StringVar()
        self.sup_contact = tk.StringVar()
        self.sup_address = tk.StringVar()
        ttk.Entry(form, textvariable=self.sup_name).grid(row=1, column=0, sticky="ew", pady=(4, 8))
        ttk.Entry(form, textvariable=self.sup_contact).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 8))
        ttk.Entry(form, textvariable=self.sup_address).grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(4, 8))
        for idx in range(3):
            form.columnconfigure(idx, weight=1)
        btns = ttk.Frame(self.suppliers_tab, style="Card.TFrame")
        btns.pack(fill="x", pady=(0, 10))
        ttk.Button(btns, text="Add Supplier", style="Primary.TButton", command=self.add_supplier).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Update Supplier", style="Primary.TButton", command=self.update_supplier).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Delete Supplier", style="Danger.TButton", command=self.delete_supplier).pack(side="left")
        self.suppliers_tree = self._create_tree(self.suppliers_tab, ("ID", "Supplier Name", "Contact", "Address"))
        self.suppliers_tree.pack(fill="both", expand=True)
        self.suppliers_tree.bind("<<TreeviewSelect>>", self.on_supplier_select)
    def _build_stockin_tab(self):
        step1 = ttk.LabelFrame(self.stockin_tab, text="1. Delivery", style="Section.TLabelframe", padding=10)
        step1.pack(fill="x", pady=(0, 8))
        ttk.Label(step1, text="Product", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(step1, text="Supplier", style="Field.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(step1, text="Quantity (kg)", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))
        ttk.Label(step1, text="Batch ID", style="Field.TLabel").grid(row=0, column=3, sticky="w", padx=(10, 0))
        self.stock_product = ttk.Combobox(step1, state="readonly")
        self.stock_supplier = ttk.Combobox(step1, state="readonly")
        self.stock_qty = tk.StringVar()
        self.stock_batch_id = tk.StringVar()
        self.stock_product.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.stock_supplier.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 0))
        ttk.Entry(step1, textvariable=self.stock_qty).grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(4, 0))
        batch_frame = ttk.Frame(step1)
        batch_frame.grid(row=1, column=3, sticky="ew", padx=(10, 0), pady=(4, 0))
        ttk.Entry(batch_frame, textvariable=self.stock_batch_id).pack(side="left", fill="x", expand=True)
        ttk.Button(batch_frame, text="Scan with QR", width=13, command=self._generate_batch_id).pack(side="left", padx=(6, 0))
        for idx in range(4):
            step1.columnconfigure(idx, weight=1)
        step2 = ttk.LabelFrame(self.stockin_tab, text="2. Cold chain check", style="Section.TLabelframe", padding=10)
        step2.pack(fill="x", pady=(0, 8))
        ttk.Label(step2, text="Arrival temp (°C)", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        self.stock_temp = tk.StringVar()
        ttk.Entry(step2, textvariable=self.stock_temp, width=14).grid(row=1, column=0, sticky="w", pady=(4, 0))
        ttk.Label(
            step2,
            text="Note: Chicken must be at or below 4°C upon arrival. Reject delivery if above 7°C.",
            style="Muted.TLabel",
        ).grid(row=2, column=0, sticky="w", pady=(8, 0))
        step2.columnconfigure(0, weight=1)
        stockin_btns = ttk.Frame(self.stockin_tab, style="Card.TFrame")
        stockin_btns.pack(fill="x", pady=(0, 10))
        ttk.Button(stockin_btns, text="Save Stock-In", style="Primary.TButton", command=self.add_stock_in).pack(side="left", padx=(0, 8))
        ttk.Button(stockin_btns, text="Update Stock-In", style="Primary.TButton", command=self.update_stock_in).pack(side="left", padx=(0, 8))
        ttk.Button(stockin_btns, text="Delete Stock-In", style="Danger.TButton", command=self.delete_stock_in).pack(side="left")
        ttk.Button(
            stockin_btns,
            text="Safety Audit",
            style="Primary.TButton",
            command=lambda: self.open_reporting_view_popup("vw_supplier_safety_audit", "Supplier Safety Audit"),
        ).pack(side="left", padx=(8, 0))
        self.stock_tree = self._create_tree(
            self.stockin_tab,
            ("ID", "Product", "Supplier", "Employee", "Qty", "Temp", "Safety", "Batch ID", "Date"),
        )
        self.stock_tree.pack(fill="both", expand=True)
        self.stock_tree.bind("<<TreeviewSelect>>", self.on_stockin_select)
    def _build_stockout_tab(self):
        intro = ttk.Label(
            self.stockout_tab,
            text="Record removals",
            style="Muted.TLabel",
        )
        intro.pack(anchor="w", pady=(0, 8))
        form = ttk.LabelFrame(self.stockout_tab, text="Stock-out entry", style="Section.TLabelframe", padding=10)
        form.pack(fill="x")
        ttk.Label(form, text="Product", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Quantity (kg)", style="Field.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(form, text="Reason", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.stockout_product = ttk.Combobox(form, state="readonly")
        self.stockout_qty = tk.StringVar()
        self.stockout_reason = ttk.Combobox(form, values=STOCKOUT_REASONS, state="normal")
        self.stockout_available_var = tk.StringVar(value="0.00 kg")
        self.stockout_product.grid(row=1, column=0, sticky="ew", pady=(4, 6))
        ttk.Entry(form, textvariable=self.stockout_qty).grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 6))
        self.stockout_reason.grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(4, 6))
        stock_badge = tk.Frame(form, bg=BG)
        stock_badge.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=(12, 0), pady=(0, 0))
        ttk.Label(stock_badge, text="Current Stock", style="StockHint.TLabel").pack(anchor="w", padx=10, pady=(7, 0))
        ttk.Label(stock_badge, textvariable=self.stockout_available_var, style="StockValue.TLabel").pack(anchor="w", padx=10, pady=(0, 7))
        self.stockout_product.bind("<<ComboboxSelected>>", self._update_stockout_available_stock)
        self.stockout_reason.bind("<<ComboboxSelected>>", lambda e: None)
        for idx in range(3):
            form.columnconfigure(idx, weight=1)
        form.columnconfigure(3, weight=0)
        btns = ttk.Frame(self.stockout_tab, style="Card.TFrame")
        btns.pack(fill="x", pady=(0, 10))
        ttk.Button(btns, text="Save Stock-Out", style="Primary.TButton", command=self.add_stock_out).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Update Stock-Out", style="Primary.TButton", command=self.update_stock_out).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Delete Stock-Out", style="Danger.TButton", command=self.delete_stock_out).pack(side="left")
        self.stockout_tree = self._create_tree(
            self.stockout_tab,
            ("ID", "Product", "Employee", "Qty", "Reason", "Date"),
        )
        self.stockout_tree.pack(fill="both", expand=True)
        self.stockout_tree.bind("<<TreeviewSelect>>", self.on_stockout_select)
    def _build_sales_tab(self):
        top = ttk.Frame(self.sales_tab, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Customer", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(top, text="Payment Method", style="Field.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(top, text="Walk-In", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.sale_customer = ttk.Combobox(top, state="readonly")
        self.sale_payment = ttk.Combobox(top, values=["Cash", "Credit"], state="readonly")
        self.sale_payment.set("Cash")
        self.sale_walkin_var = tk.BooleanVar(value=False)
        self.sale_customer_balance_var = tk.StringVar(value="Balance: N/A")
        self.sale_customer.grid(row=1, column=0, sticky="ew", pady=(4, 10))
        self.sale_payment.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 10))
        ttk.Checkbutton(top, text="Walk-in customer", variable=self.sale_walkin_var, command=self._sync_sale_customer_state).grid(
            row=1, column=2, sticky="w", padx=(10, 0), pady=(4, 10)
        )
        ttk.Label(top, textvariable=self.sale_customer_balance_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w", pady=(0, 10))
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=0)
        self.sale_payment.bind("<<ComboboxSelected>>", self._sync_sale_customer_state)
        self.sale_customer.bind("<<ComboboxSelected>>", self._update_sale_customer_balance)
        items = ttk.Frame(self.sales_tab, style="Card.TFrame")
        items.pack(fill="x")
        ttk.Label(items, text="Product", style="Field.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(items, text="Brand", style="Field.TLabel").grid(row=0, column=1, sticky="w", padx=(10, 0))
        ttk.Label(items, text="Quantity (kg)", style="Field.TLabel").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.sale_product = ttk.Combobox(items, state="readonly")
        self.sale_brand = ttk.Combobox(items, state="readonly")
        self.sale_qty = tk.StringVar()
        self.sale_available_var = tk.StringVar(value="0.00 kg")
        self.sale_size_var = tk.StringVar(value="Size: N/A")
        self.sale_product.grid(row=1, column=0, sticky="ew", pady=(4, 10))
        self.sale_brand.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(4, 10))
        ttk.Entry(items, textvariable=self.sale_qty).grid(row=1, column=2, sticky="ew", padx=(10, 0), pady=(4, 10))
        btns_frame = ttk.Frame(items)
        btns_frame.grid(row=1, column=3, padx=(10, 0))
        ttk.Button(btns_frame, text="Add Item", style="Primary.TButton", command=self.add_sale_item).pack(side="left")
        ttk.Button(btns_frame, text="Remove Item", style="Danger.TButton", command=self._delete_cart_item).pack(side="left", padx=(6, 0))
        sale_stock_badge = tk.Frame(items, bg=BG)
        sale_stock_badge.grid(row=0, column=4, rowspan=2, sticky="nsew", padx=(12, 0), pady=(0, 0))
        ttk.Label(sale_stock_badge, text="Current stock", style="StockHint.TLabel").pack(anchor="w", padx=10, pady=(7, 0))
        ttk.Label(sale_stock_badge, textvariable=self.sale_available_var, style="StockValue.TLabel").pack(anchor="w", padx=10, pady=(0, 3))
        self.sale_product.bind("<<ComboboxSelected>>", lambda e: [self._update_sale_available_stock(), self._update_sale_brands()])
        items.columnconfigure(0, weight=1)
        items.columnconfigure(1, weight=1)
        items.columnconfigure(2, weight=1)
        self.cart_tree = self._create_tree(self.sales_tab, ("Product ID", "Product", "Brand", "Size", "Qty", "Unit Price", "Subtotal"))
        self.cart_tree.pack(fill="both", expand=True)
        self.cart_tree.bind("<Delete>", self._delete_cart_item)
        self.cart_tree.bind("<Button-3>", self._cart_right_click)
        bottom = ttk.Frame(self.sales_tab, style="Card.TFrame")
        bottom.pack(fill="x", pady=(10, 0))
        self.total_var = tk.StringVar(value="Total: 0.00")
        ttk.Label(bottom, textvariable=self.total_var, style="Title.TLabel").pack(side="left")
        ttk.Button(bottom, text="Finalize Sale", style="Primary.TButton", command=self.finalize_sale).pack(side="right")
        ttk.Button(bottom, text="Clear Cart", style="Danger.TButton", command=self.clear_cart).pack(side="right", padx=(0, 8))
        history_top = ttk.Frame(self.sales_tab, style="Card.TFrame")
        history_top.pack(fill="x", pady=(14, 6))
        ttk.Label(history_top, text="Sales History", style="Field.TLabel").pack(side="left")
        ttk.Button(history_top, text="Open Sales History", style="Primary.TButton", command=self.open_sales_history_popup).pack(side="right")
        ttk.Button(
            history_top,
            text="Detailed Sales",
            style="Primary.TButton",
            command=lambda: self.open_reporting_view_popup("vw_detailed_sales", "Detailed Sales"),
        ).pack(side="right", padx=(0, 8))

    def open_sales_history_popup(self):
        if self.sales_history_window is not None and self.sales_history_window.winfo_exists():
            self.sales_history_window.lift()
            self.sales_history_window.focus_force()
            self.refresh_sales_history()
            return
        popup = tk.Toplevel(self)
        popup.title("Sales History")
        popup.geometry("1180x560")
        popup.configure(bg=BG)
        popup.transient(self)
        popup.grab_set()
        self.sales_history_window = popup
        top = ttk.Frame(popup, style="Card.TFrame", padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Sales History", style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Refresh", style="Primary.TButton", command=self.refresh_sales_history).pack(side="right")
        ttk.Button(top, text="View Record", style="Primary.TButton", command=self.view_selected_sale_record).pack(side="right", padx=(0, 8))
        ttk.Button(top, text="Delete Selected Sale", style="Danger.TButton", command=self.delete_sale).pack(side="right", padx=(0, 8))
        table_wrap = ttk.Frame(popup, style="Card.TFrame", padding=(10, 0, 10, 10))
        table_wrap.pack(fill="both", expand=True)
        self.sales_history_tree = self._create_tree(
            table_wrap,
            ("Sale ID", "Date", "Customer", "Employee ID", "Employee", "Payment", "Items Added", "Total"),
        )
        self.sales_history_tree.column("Items Added", anchor="w", width=420)
        self.sales_history_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll = ttk.Scrollbar(table_wrap, orient="vertical", command=self.sales_history_tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.sales_history_tree.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.sales_history_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        table_wrap.columnconfigure(0, weight=1)
        table_wrap.rowconfigure(0, weight=1)
        def _on_close():
            self.sales_history_window = None
            self.sales_history_tree = None
            popup.destroy()
        popup.protocol("WM_DELETE_WINDOW", _on_close)
        self.refresh_sales_history()
    def open_reporting_view_popup(self, view_name, title):
        popup = tk.Toplevel(self)
        popup.title(title)
        popup.geometry("1180x560")
        popup.configure(bg=BG)
        popup.transient(self)
        top = ttk.Frame(popup, style="Card.TFrame", padding=10)
        top.pack(fill="x")
        ttk.Label(top, text=title, style="Title.TLabel").pack(side="left")
        ttk.Button(top, text="Refresh", style="Primary.TButton", command=lambda: self._load_reporting_popup_tree(tree, view_name)).pack(side="right")
        body = ttk.Frame(popup, style="Card.TFrame", padding=(10, 0, 10, 10))
        body.pack(fill="both", expand=True)
        tree = ttk.Treeview(body)
        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll = ttk.Scrollbar(body, orient="vertical", command=tree.yview)
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll = ttk.Scrollbar(body, orient="horizontal", command=tree.xview)
        x_scroll.grid(row=1, column=0, sticky="ew")
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)
        self._load_reporting_popup_tree(tree, view_name)
    def _load_reporting_popup_tree(self, tree, view_name):
        cols, rows = self._get_browser_dataset(view_name)
        for item in tree.get_children():
            tree.delete(item)
        tree["columns"] = cols
        tree["show"] = "headings"
        for col in cols:
            label = prettify_column_name(view_name, col)
            tree.heading(col, text=label)
            tree.column(col, width=max(140, len(label) * 10), anchor="center")
        for row in rows:
            tree.insert("", "end", values=row)
    def _build_dashboard_tab(self):
        hero = tk.Frame(self.dashboard_tab, bg=CARD, highlightbackground=BG, highlightthickness=1)
        hero.pack(fill="x", pady=(0, 14))
        hero_left = tk.Frame(hero, bg=CARD)
        hero_left.pack(side="left", fill="both", expand=True, padx=20, pady=18)
        tk.Label(hero_left, text="Dashboard", bg=CARD, fg=TEXT, font=("Segoe UI", 22, "bold"), anchor="w").pack(anchor="w")
        self.dashboard_summary_var = tk.StringVar(value="Loading dashboard...")
        tk.Label(
            hero_left,
            textvariable=self.dashboard_summary_var,
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 10),
            anchor="w",
            justify="left",
        ).pack(anchor="w", pady=(8, 4))
        self.dashboard_focus_var = tk.StringVar(value="Gathering cash flow and activity signals...")
        tk.Label(hero_left, textvariable=self.dashboard_focus_var, bg=CARD, fg=NAVY, font=("Segoe UI", 9, "bold"), anchor="w").pack(anchor="w")
        hero_right = tk.Frame(hero, bg=CARD)
        hero_right.pack(side="right", padx=18, pady=18)
        self.dashboard_date_var = tk.StringVar(value=date.today().strftime("%B %d, %Y"))
        tk.Label(hero_right, text="TODAY", bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=14, pady=(12, 0))
        tk.Label(hero_right, textvariable=self.dashboard_date_var, bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(0, 12))
        ttk.Button(hero_right, text="Refresh Dashboard", style="Primary.TButton", command=self.refresh_dashboard).pack(anchor="w", padx=14, pady=(0, 12))
        stats = tk.Frame(self.dashboard_tab, bg=CARD)
        stats.pack(fill="x", pady=(0, 14))
        for idx in range(4):
            stats.grid_columnconfigure(idx, weight=1)
        self.dashboard_stat_vars = {
            "products": tk.StringVar(value="0"),
            "stock": tk.StringVar(value="0.00 kg"),
            "sales": tk.StringVar(value="0.00"),
            "alerts": tk.StringVar(value="0"),
            "products_meta": tk.StringVar(value="registered items"),
            "stock_meta": tk.StringVar(value="current inventory"),
            "sales_meta": tk.StringVar(value="total revenue"),
            "alerts_meta": tk.StringVar(value="out-of-stock items"),
        }
        stat_specs = (
            ("Catalog", "products", "products_meta", "#F7FAFC", NAVY, TEXT),
            ("Inventory", "stock", "stock_meta", "#F8FBF7", "#2E7D32", TEXT),
            ("Revenue", "sales", "sales_meta", "#FFF8F2", "#B36B00", TEXT),
            ("Alerts", "alerts", "alerts_meta", "#FFF5F5", ACCENT, TEXT),
        )
        for idx, (title, value_key, meta_key, bg_color, accent_color, text_color) in enumerate(stat_specs):
            card = tk.Frame(stats, bg=bg_color, highlightbackground=BG, highlightthickness=1)
            card.grid(row=0, column=idx, sticky="nsew", padx=(0 if idx == 0 else 6, 0 if idx == len(stat_specs) - 1 else 6))
            tk.Frame(card, bg=accent_color, height=4).pack(fill="x")
            body = tk.Frame(card, bg=bg_color)
            body.pack(fill="both", expand=True, padx=14, pady=14)
            tk.Label(body, text=title.upper(), bg=bg_color, fg=accent_color, font=("Segoe UI", 8, "bold")).pack(anchor="w")
            tk.Label(body, textvariable=self.dashboard_stat_vars[value_key], bg=bg_color, fg=text_color, font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(8, 4))
            tk.Label(body, textvariable=self.dashboard_stat_vars[meta_key], bg=bg_color, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
        section_bar = tk.Frame(self.dashboard_tab, bg=CARD)
        section_bar.pack(fill="x", pady=(0, 10))
        tk.Label(section_bar, text="Recent sales", bg=CARD, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(side="left")
        tk.Label(
            section_bar,
            text="",
            bg=CARD,
            fg=MUTED,
            font=("Segoe UI", 9),
        ).pack(side="left", padx=(10, 0), pady=(4, 0))
        panel_bg = "#FCFDFF"
        sales_wrap = tk.Frame(self.dashboard_tab, bg=panel_bg, highlightbackground=BG, highlightthickness=1)
        sales_wrap.pack(fill="both", expand=True)
        sales_head = tk.Frame(sales_wrap, bg=panel_bg)
        sales_head.pack(fill="x")
        tk.Label(sales_head, text="Latest sales", bg=panel_bg, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(side="left", padx=10, pady=(10, 0))
        self.dashboard_sales_hint_var = tk.StringVar(value="Waiting for sales activity...")
        tk.Label(sales_head, textvariable=self.dashboard_sales_hint_var, bg=panel_bg, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=10, pady=(12, 0))
        self.dashboard_sales_tree = self._create_tree(sales_wrap, ("Customer", "Amount"))
        self.dashboard_sales_tree.configure(height=18)
        self.dashboard_sales_tree.pack(fill="both", expand=True, padx=10, pady=(10, 10))
    def _create_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="extended")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        return tree
    def _to_decimal(self, value: str, label: str):
        try:
            return Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError(f"Invalid {label}.")
    def _next_available_id(self, cursor, table_name: str, pk_column: str):
        cursor.execute(f"SELECT {pk_column} FROM {table_name} ORDER BY {pk_column} ASC")
        next_id = 1
        for row in cursor.fetchall():
            if isinstance(row, dict):
                current_id = row[pk_column]
            else:
                current_id = row[0]
            if current_id != next_id:
                break
            next_id += 1
        return next_id
    def _selected_ids(self, tree):
        return [int(tree.item(item_id, "values")[0]) for item_id in tree.selection()]
    def _stock_in_is_accepted(self, arrival_temp: Decimal):
        return arrival_temp <= Decimal("5.0")

    def _get_product_id_from_combo(self, combo):
        if not combo.get():
            return None
        return int(combo.get().split(" - ", 1)[0])
    def _set_combo_by_id(self, combo, record_id):
        record_prefix = f"{record_id} - "
        for value in combo.cget("values"):
            if value.startswith(record_prefix):
                combo.set(value)
                return
    def _get_customer_id_from_combo(self, combo):
        if not combo.get():
            return None
        return int(combo.get().split(" - ", 1)[0])
    def _sync_sale_customer_state(self, _event=None):
        if self.sale_walkin_var.get():
            self.sale_payment.set("Cash")
            self.sale_customer.set("")
            self.sale_customer.configure(state="disabled")
            self.sale_customer_balance_var.set("Balance: N/A")
            return
        self.sale_customer.configure(state="readonly")
        if self.sale_payment.get().strip() == "Credit" and not self.sale_customer.get():
            values = list(self.sale_customer.cget("values"))
            if len(values) > 1:
                self.sale_customer.set(values[1])
        self._update_sale_customer_balance()
    def _update_sale_customer_balance(self, _event=None):
        customer_id = self._get_customer_id_from_combo(self.sale_customer)
        if customer_id is None:
            self.sale_customer_balance_var.set("Balance: N/A")
            return
        balance = self.customer_balance_by_id.get(customer_id, Decimal("0.00"))
        self.sale_customer_balance_var.set(f"Balance: {balance}")
    def _get_supplier_id_from_combo(self, combo):
        if not combo.get():
            return None
        return int(combo.get().split(" - ", 1)[0])
    def _update_stockout_available_stock(self, _event=None):
        self._set_product_stock_label(self.stockout_product, self.stockout_available_var)

    def _update_sale_available_stock(self, _event=None):
        self._set_product_stock_label(self.sale_product, self.sale_available_var)
    def _refresh_dropdowns(self):
        with db_cursor(dictionary=True) as (_, cursor):
            cursor.execute("SELECT product_id, product_name FROM products ORDER BY product_id ASC")
            products = cursor.fetchall()
            cursor.execute("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_id ASC")
            suppliers = cursor.fetchall()
            cursor.execute(
                """
                SELECT
                    customer_id,
                    current_bal,
                    CASE
                        WHEN is_business = 1 THEN business_name
                        ELSE TRIM(CONCAT_WS(' ', first_name, middle_name, last_name))
                    END AS customer_display_name
                FROM customers
                WHERE CASE
                    WHEN is_business = 1 THEN business_name
                    ELSE TRIM(CONCAT_WS(' ', first_name, middle_name, last_name))
                END != 'Walk-in Customer'
                ORDER BY customer_id ASC
                """
            )
            customers = cursor.fetchall()
        product_values = [f"{r['product_id']} - {r['product_name']}" for r in products]
        supplier_values = [f"{r['supplier_id']} - {r['supplier_name']}" for r in suppliers]
        customer_values = [""] + [f"{r['customer_id']} - {r['customer_display_name']}" for r in customers]
        self.customer_balance_by_id = {
            r["customer_id"]: (r["current_bal"] if r["current_bal"] is not None else Decimal("0.00")) for r in customers
        }
        self.stock_product["values"] = product_values
        self.stock_supplier["values"] = supplier_values
        self.stockout_product["values"] = product_values
        self.sale_product["values"] = product_values
        self.sale_customer["values"] = customer_values
        if product_values and not self.stock_product.get():
            self.stock_product.set(product_values[0])
        if supplier_values and not self.stock_supplier.get():
            self.stock_supplier.set(supplier_values[0])
        if product_values and not self.stockout_product.get():
            self.stockout_product.set(product_values[0])
        if product_values and not self.sale_product.get():
            self.sale_product.set(product_values[0])
        if not self.sale_walkin_var.get():
            if self.sale_payment.get().strip() == "Credit" and len(customer_values) > 1 and not self.sale_customer.get():
                self.sale_customer.set(customer_values[1])
            elif not self.sale_customer.get():
                self.sale_customer.set("")
        self._sync_sale_customer_state()
        self._update_stockout_available_stock()
        self._update_sale_available_stock()
        self._update_sale_customer_balance()
    def on_product_select(self, _event=None):
        selected = self.products_tree.selection()
        if not selected:
            return
        values = self.products_tree.item(selected[0], "values")
        self.p_name.set(values[1])
        self.p_brand.set(values[2])
        self.p_size.set(values[3])
        self.p_price.set(values[4])
    def on_employee_select(self, _event=None):
        selected = self.employees_tree.selection()
        if not selected:
            return
        values = self.employees_tree.item(selected[0], "values")
        self.e_name.set(values[1])
        self.e_username.set(values[2])
        self.e_password.set("")
        self.e_role.set(values[3])
        if values[4]:
            self.e_date_hired.set_date(values[4])
        else:
            self.e_date_hired.clear()
    def _normalize_date_hired(self, value):
        value = str(value).strip()
        if not value:
            return None
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as err:
            raise ValueError("Date hired must use YYYY-MM-DD format.") from err
    def _toggle_customer_name_mode(self):
        is_business = bool(self.c_is_business.get())
        person_state = "disabled" if is_business else "normal"
        business_state = "normal" if is_business else "disabled"
        self.c_first_name_entry.configure(state=person_state)
        self.c_middle_name_entry.configure(state=person_state)
        self.c_last_name_entry.configure(state=person_state)
        self.c_business_name_entry.configure(state=business_state)
    def _compose_customer_payload(self):
        is_business = bool(self.c_is_business.get())
        contact = self.c_contact.get().strip() or None
        debt = self._to_decimal(self.c_debt.get().strip() or "0", "customer balance")
        if is_business:
            business_name = self.c_business_name.get().strip()
            if not business_name:
                raise ValueError("Business name is required when Business Name is checked.")
            return {
                "is_business": 1,
                "first_name": None,
                "middle_name": None,
                "last_name": None,
                "business_name": business_name,
                "contact": contact,
                "debt": debt,
            }
        first = self.c_first_name.get().strip()
        middle = self.c_middle_name.get().strip()
        last = self.c_last_name.get().strip()
        if not first or not last:
            raise ValueError("First name and last name are required.")
        return {
            "is_business": 0,
            "first_name": first,
            "middle_name": middle or None,
            "last_name": last,
            "business_name": None,
            "contact": contact,
            "debt": debt,
        }
    def on_customer_select(self, _event=None):
        selected = self.customers_tree.selection()
        if not selected:
            return
        customer_id = int(self.customers_tree.item(selected[0], "values")[0])
        with db_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT contact_num, first_name, middle_name, last_name, business_name, is_business, current_bal
                FROM customers
                WHERE customer_id = %s
                """,
                (customer_id,),
            )
            row = cursor.fetchone()
        if not row:
            return
        self.c_is_business.set(1 if row["is_business"] else 0)
        if row["is_business"]:
            self.c_first_name.set("")
            self.c_middle_name.set("")
            self.c_last_name.set("")
            self.c_business_name.set(row["business_name"] or "")
        else:
            first = row["first_name"] or ""
            middle = row["middle_name"] or ""
            last = row["last_name"] or ""
            self.c_first_name.set(first)
            self.c_middle_name.set(middle)
            self.c_last_name.set(last)
            self.c_business_name.set("")
        self.c_contact.set(row["contact_num"] or "")
        self.c_debt.set(str(row["current_bal"] if row["current_bal"] is not None else "0.00"))
        self._toggle_customer_name_mode()
    def on_supplier_select(self, _event=None):
        selected = self.suppliers_tree.selection()
        if not selected:
            return
        values = self.suppliers_tree.item(selected[0], "values")
        self.sup_name.set(values[1])
        self.sup_contact.set(values[2])
        self.sup_address.set(values[3])
    def on_stockin_select(self, _event=None):
        selected = self.stock_tree.selection()
        if not selected:
            return
        stockin_id = int(self.stock_tree.item(selected[0], "values")[0])
        with db_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT product_id, supplier_id, quantity_kg, arrival_temp, batch_id
                FROM stock_in
                WHERE stockin_id = %s
                """,
                (stockin_id,),
            )
            row = cursor.fetchone()
        if not row:
            return
        self._set_combo_by_id(self.stock_product, row["product_id"])
        self._set_combo_by_id(self.stock_supplier, row["supplier_id"])
        self.stock_qty.set(str(row["quantity_kg"]))
        self.stock_temp.set(str(row["arrival_temp"]))
        self.stock_batch_id.set(row["batch_id"] or "")
    def on_stockout_select(self, _event=None):
        selected = self.stockout_tree.selection()
        if not selected:
            return
        stockout_id = int(self.stockout_tree.item(selected[0], "values")[0])
        with db_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT product_id, quantity_kg, reason
                FROM stock_out
                WHERE stockout_id = %s
                """,
                (stockout_id,),
            )
            row = cursor.fetchone()
        if not row:
            return
        self._set_combo_by_id(self.stockout_product, row["product_id"])
        self.stockout_qty.set(str(row["quantity_kg"]))
        self.stockout_reason.set(row["reason"] or "")
        self._update_stockout_available_stock()
    def add_product(self):
        try:
            name = self.p_name.get().strip()
            brand = self.p_brand.get().strip() or random.choice(
                ["FarmFresh", "CluckGold", "HenHouse", "DailyRoost", "PrimePoultry", "SunriseFowl", "FeatherBest", "MarketBird"]
            )
            size = self.p_size.get().strip() or "Regular"
            price = self._to_decimal(self.p_price.get().strip(), "unit price")
            if not name:
                raise ValueError("Product name is required.")
            with db_cursor() as (conn, cursor):
                product_id = self._next_available_id(cursor, "products", "product_id")
                cursor.execute(
                    "INSERT INTO products (product_id, product_name, brand, size, unit_price, stock_quantity, reorder_point) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (product_id, name, brand, size, price, Decimal("0.00"), Decimal("10.00")),
                )
                conn.commit()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", "Product added. Use Stock-In to add inventory.")
        except (ValueError, Error) as err:
            messagebox.showerror("Error", str(err))
    def update_product(self):
        selected = self.products_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a product first.")
            return
        product_id = int(self.products_tree.item(selected[0], "values")[0])
        try:
            name = self.p_name.get().strip()
            brand = self.p_brand.get().strip() or random.choice(
                ["FarmFresh", "CluckGold", "HenHouse", "DailyRoost", "PrimePoultry", "SunriseFowl", "FeatherBest", "MarketBird"]
            )
            size = self.p_size.get().strip() or "Regular"
            price = self._to_decimal(self.p_price.get().strip(), "unit price")
            if not name:
                raise ValueError("Product name is required.")
            with db_cursor(dictionary=True) as (conn, cursor):
                cursor.execute("SELECT reorder_point FROM products WHERE product_id = %s", (product_id,))
                existing = cursor.fetchone()
                if not existing:
                    raise ValueError("Product not found.")
                cursor.execute(
                    "UPDATE products SET product_name = %s, brand = %s, size = %s, unit_price = %s, reorder_point = %s WHERE product_id = %s",
                    (name, brand, size, price, existing["reorder_point"], product_id),
                )
                conn.commit()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", "Product updated. Use Stock-In or Stock-Out to change stock.")
        except (ValueError, Error) as err:
            messagebox.showerror("Error", str(err))
    def delete_product(self):
        product_ids = self._selected_ids(self.products_tree)
        if not product_ids:
            messagebox.showwarning("No Selection", "Select one or more products first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(product_ids)} selected product(s)?"):
            return
        try:
            with db_cursor() as (conn, cursor):
                for product_id in product_ids:
                    cursor.execute(
                        """
                        SELECT
                            (SELECT COUNT(*) FROM stock_in WHERE product_id = %s) AS stockin_refs,
                            (SELECT COUNT(*) FROM stock_out WHERE product_id = %s) AS stockout_refs,
                            (SELECT COUNT(*) FROM sale_items WHERE product_id = %s) AS sale_item_refs
                        """,
                        (product_id, product_id, product_id),
                    )
                    refs = cursor.fetchone()
                    stockin_refs, stockout_refs, sale_item_refs = refs
                    if stockin_refs or stockout_refs or sale_item_refs:
                        raise ValueError(
                            "Cannot delete product ID {0} because it is still referenced by "
                            "{1} stock-in record(s), {2} stock-out record(s), and {3} sale item record(s). "
                            "Delete the related transactions first.".format(
                                product_id,
                                stockin_refs,
                                stockout_refs,
                                sale_item_refs,
                            )
                        )
                    cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
                conn.commit()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", f"{len(product_ids)} product(s) deleted.")
        except (ValueError, Error) as err:
            messagebox.showerror("Error", str(err))
    def add_customer(self):
        try:
            payload = self._compose_customer_payload()
        except ValueError as err:
            messagebox.showwarning("Missing Data", str(err))
            return
        try:
            with db_cursor() as (conn, cursor):
                customer_id = self._next_available_id(cursor, "customers", "customer_id")
                cursor.execute(
                    """
                    INSERT INTO customers (
                        customer_id, contact_num, first_name, middle_name, last_name, business_name, is_business, current_bal
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        customer_id,
                        payload["contact"],
                        payload["first_name"],
                        payload["middle_name"],
                        payload["last_name"],
                        payload["business_name"],
                        payload["is_business"],
                        payload["debt"],
                    ),
                )
                conn.commit()
            self.refresh_customers()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", "Customer added.")
        except Error as err:
            messagebox.showerror("Error", str(err))
    def update_customer(self):
        selected = self.customers_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a customer first.")
            return
        customer_id = int(self.customers_tree.item(selected[0], "values")[0])
        try:
            payload = self._compose_customer_payload()
        except ValueError as err:
            messagebox.showwarning("Missing Data", str(err))
            return
        try:
            with db_cursor() as (conn, cursor):
                cursor.execute(
                    """
                    UPDATE customers
                    SET contact_num = %s,
                        first_name = %s,
                        middle_name = %s,
                        last_name = %s,
                        business_name = %s,
                        is_business = %s,
                        current_bal = %s
                    WHERE customer_id = %s
                    """,
                    (
                        payload["contact"],
                        payload["first_name"],
                        payload["middle_name"],
                        payload["last_name"],
                        payload["business_name"],
                        payload["is_business"],
                        payload["debt"],
                        customer_id,
                    ),
                )
                conn.commit()
            self.refresh_customers()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", "Customer updated.")
        except Error as err:
            messagebox.showerror("Error", str(err))
    def delete_customer(self):
        customer_ids = self._selected_ids(self.customers_tree)
        if not customer_ids:
            messagebox.showwarning("No Selection", "Select one or more customers first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(customer_ids)} selected customer(s)?"):
            return
        try:
            with db_cursor() as (conn, cursor):
                for customer_id in customer_ids:
                    cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
                conn.commit()
            self.refresh_customers()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", f"{len(customer_ids)} customer(s) deleted.")
        except Error as err:
            messagebox.showerror("Error", str(err))
    def add_supplier(self):
        try:
            supplier_name = self.sup_name.get().strip()
            contact = self.sup_contact.get().strip()
            address = self.sup_address.get().strip()
            if not supplier_name or not contact:
                raise ValueError("Supplier name and contact are required.")
            with db_cursor() as (conn, cursor):
                supplier_id = self._next_available_id(cursor, "suppliers", "supplier_id")
                cursor.execute(
                    "INSERT INTO suppliers (supplier_id, supplier_name, contact, address) VALUES (%s, %s, %s, %s)",
                    (supplier_id, supplier_name, contact, address or None),
                )
                conn.commit()
            self.sup_name.set("")
            self.sup_contact.set("")
            self.sup_address.set("")
            self.refresh_all()
            messagebox.showinfo("Success", "Supplier added.")
        except (ValueError, Error) as err:
            messagebox.showerror("Error", str(err))
    def update_supplier(self):
        selected = self.suppliers_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a supplier first.")
            return
        supplier_id = int(self.suppliers_tree.item(selected[0], "values")[0])
        try:
            supplier_name = self.sup_name.get().strip()
            contact = self.sup_contact.get().strip()
            address = self.sup_address.get().strip()
            if not supplier_name or not contact:
                raise ValueError("Supplier name and contact are required.")
            with db_cursor() as (conn, cursor):
                cursor.execute(
                    "UPDATE suppliers SET supplier_name = %s, contact = %s, address = %s WHERE supplier_id = %s",
                    (supplier_name, contact, address or None, supplier_id),
                )
                conn.commit()
            self.refresh_all()
            messagebox.showinfo("Success", "Supplier updated.")
        except (ValueError, Error) as err:
            messagebox.showerror("Error", str(err))
    def delete_supplier(self):
        supplier_ids = self._selected_ids(self.suppliers_tree)
        if not supplier_ids:
            messagebox.showwarning("No Selection", "Select one or more suppliers first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(supplier_ids)} selected supplier(s)?"):
            return
        try:
            with db_cursor() as (conn, cursor):
                for supplier_id in supplier_ids:
                    cursor.execute("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
                conn.commit()
            self.sup_name.set("")
            self.sup_contact.set("")
            self.sup_address.set("")
            self.refresh_all()
            messagebox.showinfo("Success", f"{len(supplier_ids)} supplier(s) deleted.")
        except Error as err:
            messagebox.showerror("Error", str(err))
    def add_employee(self):
        try:
            name = self.e_name.get().strip()
            username = self.e_username.get().strip()
            password = self.e_password.get().strip()
            role = self.e_role.get().strip()
            date_hired = self._normalize_date_hired(self.e_date_hired.get())
            if not all((name, username, password, role)):
                raise ValueError("Name, username, password, and role are required.")
            with db_cursor() as (conn, cursor):
                employee_id = self._next_available_id(cursor, "employees", "employee_id")
                cursor.execute(
                    "INSERT INTO employees (employee_id, name, username, password, role, date_hired) VALUES (%s, %s, %s, %s, %s, %s)",
                    (employee_id, name, username, password, role, date_hired),
                )
                conn.commit()
            self.refresh_employees()
            messagebox.showinfo("Success", "Employee added.")
        except (ValueError, Error) as err:
            messagebox.showerror("Employee Error", str(err))
    def update_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select an employee first.")
            return
        employee_id = int(self.employees_tree.item(selected[0], "values")[0])
        try:
            name = self.e_name.get().strip()
            username = self.e_username.get().strip()
            password = self.e_password.get().strip()
            role = self.e_role.get().strip()
            date_hired = self._normalize_date_hired(self.e_date_hired.get())
            if not all((name, username, role)):
                raise ValueError("Name, username, and role are required.")
            with db_cursor() as (conn, cursor):
                if password:
                    cursor.execute(
                        "UPDATE employees SET name = %s, username = %s, password = %s, role = %s, date_hired = %s WHERE employee_id = %s",
                        (name, username, password, role, date_hired, employee_id),
                    )
                else:
                    cursor.execute(
                        "UPDATE employees SET name = %s, username = %s, role = %s, date_hired = %s WHERE employee_id = %s",
                        (name, username, role, date_hired, employee_id),
                    )
                conn.commit()
            self.refresh_employees()
            messagebox.showinfo("Success", "Employee updated.")
        except (ValueError, Error) as err:
            messagebox.showerror("Employee Error", str(err))
    def delete_employee(self):
        employee_ids = self._selected_ids(self.employees_tree)
        if not employee_ids:
            messagebox.showwarning("No Selection", "Select one or more employees first.")
            return
        if self.user and self.user["employee_id"] in employee_ids:
            messagebox.showwarning("Invalid Action", "You cannot delete your own active account.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(employee_ids)} selected employee(s)?"):
            return
        try:
            with db_cursor() as (conn, cursor):
                for employee_id in employee_ids:
                    cursor.execute("DELETE FROM employees WHERE employee_id = %s", (employee_id,))
                conn.commit()
            self.refresh_employees()
            messagebox.showinfo("Success", f"{len(employee_ids)} employee(s) deleted.")
        except Error as err:
            messagebox.showerror("Employee Error", str(err))
    def _generate_batch_id(self):
        """Generate a batch ID: BATCH-YYYYMMDD-XXXXX (X = random digits)"""
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        random_suffix = str(random.randint(10000, 99999))
        batch_id = f"BATCH-{date_str}-{random_suffix}"
        self.stock_batch_id.set(batch_id)
    def add_stock_in(self):
        try:
            product_id = self._get_product_id_from_combo(self.stock_product)
            supplier_id = self._get_supplier_id_from_combo(self.stock_supplier)
            qty = self._to_decimal(self.stock_qty.get().strip(), "quantity")
            temp = self._to_decimal(self.stock_temp.get().strip(), "arrival temperature")
            batch_id = self.stock_batch_id.get().strip() or None
            if not product_id or not supplier_id:
                raise ValueError("Select product and supplier.")
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero.")
            with db_cursor() as (conn, cursor):
                stockin_id = self._next_available_id(cursor, "stock_in", "stockin_id")
                cursor.execute(
                    """
                    INSERT INTO stock_in (stockin_id, product_id, supplier_id, employee_id, quantity_kg, arrival_temp, batch_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (stockin_id, product_id, supplier_id, self.user["employee_id"], qty, temp, batch_id),
                )
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                    (qty, product_id),
                )
                conn.commit()
            self.stock_qty.set("")
            self.stock_temp.set("")
            self.stock_batch_id.set("")
            self.refresh_stock_in()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", "Stock-in saved.")
        except (ValueError, Error) as err:
            messagebox.showerror("Stock-In Error", str(err))
    def update_stock_in(self):
        selected = self.stock_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a stock-in record first.")
            return
        stockin_id = int(self.stock_tree.item(selected[0], "values")[0])
        try:
            product_id = self._get_product_id_from_combo(self.stock_product)
            supplier_id = self._get_supplier_id_from_combo(self.stock_supplier)
            qty = self._to_decimal(self.stock_qty.get().strip(), "quantity")
            temp = self._to_decimal(self.stock_temp.get().strip(), "arrival temperature")
            batch_id = self.stock_batch_id.get().strip() or None
            if not product_id or not supplier_id:
                raise ValueError("Select product and supplier.")
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero.")
            if temp > Decimal("7.0"):
                raise ValueError("arrival temperature exceeds 7.0°C.")
            with db_cursor(dictionary=True) as (conn, cursor):
                cursor.execute("SELECT product_id, quantity_kg, arrival_temp FROM stock_in WHERE stockin_id = %s", (stockin_id,))
                existing = cursor.fetchone()
                if not existing:
                    raise ValueError("Stock-in record not found.")
                existing_accepted = self._stock_in_is_accepted(Decimal(str(existing["arrival_temp"])))
                cursor.execute("SELECT stock_quantity FROM products WHERE product_id = %s", (existing["product_id"],))
                old_product_row = cursor.fetchone()
                if not old_product_row:
                    raise ValueError("Product not found.")
                if existing_accepted:
                    if existing["product_id"] == product_id:
                        available_after_reversal = Decimal(str(old_product_row["stock_quantity"])) + qty
                        if available_after_reversal < existing["quantity_kg"]:
                            raise ValueError("Not enough stock to update stock-in record.")
                    elif Decimal(str(old_product_row["stock_quantity"])) < existing["quantity_kg"]:
                        raise ValueError("Not enough stock to update stock-in record.")
                cursor.execute(
                    """
                    UPDATE stock_in
                    SET product_id = %s, supplier_id = %s, quantity_kg = %s, arrival_temp = %s, batch_id = %s
                    WHERE stockin_id = %s
                    """,
                    (product_id, supplier_id, qty, temp, batch_id, stockin_id),
                )
                if existing_accepted:
                    cursor.execute(
                        "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                        (existing["quantity_kg"], existing["product_id"]),
                    )
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                    (qty, product_id),
                )
                conn.commit()
            self.refresh_stock_in()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", "Stock-in updated.")
        except (ValueError, Error) as err:
            messagebox.showerror("Stock-In Error", str(err))
    def delete_stock_in(self):
        stockin_ids = self._selected_ids(self.stock_tree)
        if not stockin_ids:
            messagebox.showwarning("No Selection", "Select one or more stock-in records first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(stockin_ids)} selected stock-in record(s)?"):
            return
        try:
            with db_cursor(dictionary=True) as (conn, cursor):
                for stockin_id in stockin_ids:
                    cursor.execute("SELECT product_id, quantity_kg, arrival_temp FROM stock_in WHERE stockin_id = %s", (stockin_id,))
                    existing = cursor.fetchone()
                    if not existing:
                        raise ValueError("Stock-in record not found.")
                    existing_accepted = self._stock_in_is_accepted(Decimal(str(existing["arrival_temp"])))
                    if existing_accepted:
                        cursor.execute("SELECT stock_quantity FROM products WHERE product_id = %s", (existing["product_id"],))
                        product_row = cursor.fetchone()
                        if not product_row or product_row["stock_quantity"] < existing["quantity_kg"]:
                            raise ValueError("Cannot delete this stock-in record because some or all of that stock has already been used.")
                    cursor.execute("DELETE FROM stock_in WHERE stockin_id = %s", (stockin_id,))
                    if existing_accepted:
                        cursor.execute(
                            "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                            (existing["quantity_kg"], existing["product_id"]),
                        )
                conn.commit()
            self.refresh_stock_in()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", f"{len(stockin_ids)} stock-in record(s) deleted.")
        except (ValueError, Error) as err:
            messagebox.showerror("Error", str(err))
    def add_stock_out(self):
        try:
            product_id = self._get_product_id_from_combo(self.stockout_product)
            qty = self._to_decimal(self.stockout_qty.get().strip(), "quantity")
            reason = self.stockout_reason.get().strip()
            if not product_id:
                raise ValueError("Select a product.")
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero.")
            if not reason:
                raise ValueError("Reason is required.")
            with db_cursor(dictionary=True) as (conn, cursor):
                cursor.execute("SELECT stock_quantity FROM products WHERE product_id = %s", (product_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Product not found.")
                if row["stock_quantity"] < qty:
                    raise ValueError("Insufficient stock for stock-out.")
                stockout_id = self._next_available_id(cursor, "stock_out", "stockout_id")
                cursor.execute(
                    """
                    INSERT INTO stock_out (stockout_id, product_id, employee_id, quantity_kg, reason)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (stockout_id, product_id, self.user["employee_id"], qty, reason),
                )
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                    (qty, product_id),
                )
                conn.commit()
            self.stockout_qty.set("")
            self.stockout_reason.set("")
            self.refresh_stock_out()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", "Stock-out saved.")
        except (ValueError, Error) as err:
            messagebox.showerror("Stock-Out Error", str(err))
    def update_stock_out(self):
        selected = self.stockout_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a stock-out record first.")
            return
        stockout_id = int(self.stockout_tree.item(selected[0], "values")[0])
        try:
            product_id = self._get_product_id_from_combo(self.stockout_product)
            qty = self._to_decimal(self.stockout_qty.get().strip(), "quantity")
            reason = self.stockout_reason.get().strip()
            if not product_id:
                raise ValueError("Select a product.")
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero.")
            if not reason:
                raise ValueError("Reason is required.")
            with db_cursor(dictionary=True) as (conn, cursor):
                cursor.execute("SELECT product_id, quantity_kg FROM stock_out WHERE stockout_id = %s", (stockout_id,))
                existing = cursor.fetchone()
                if not existing:
                    raise ValueError("Stock-out record not found.")
                cursor.execute("SELECT stock_quantity FROM products WHERE product_id = %s", (product_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Product not found.")
                available = row["stock_quantity"] + existing["quantity_kg"] if existing["product_id"] == product_id else row["stock_quantity"]
                if available < qty:
                    raise ValueError("Insufficient stock for stock-out update.")
                cursor.execute(
                    """
                    UPDATE stock_out
                    SET product_id = %s, quantity_kg = %s, reason = %s
                    WHERE stockout_id = %s
                    """,
                    (product_id, qty, reason, stockout_id),
                )
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                    (existing["quantity_kg"], existing["product_id"]),
                )
                cursor.execute(
                    "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id = %s",
                    (qty, product_id),
                )
                conn.commit()
            self.refresh_stock_out()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", "Stock-out updated.")
        except (ValueError, Error) as err:
            messagebox.showerror("Stock-Out Error", str(err))
    def delete_stock_out(self):
        stockout_ids = self._selected_ids(self.stockout_tree)
        if not stockout_ids:
            messagebox.showwarning("No Selection", "Select one or more stock-out records first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(stockout_ids)} selected stock-out record(s)?"):
            return
        try:
            with db_cursor(dictionary=True) as (conn, cursor):
                for stockout_id in stockout_ids:
                    cursor.execute("SELECT product_id, quantity_kg FROM stock_out WHERE stockout_id = %s", (stockout_id,))
                    existing = cursor.fetchone()
                    if not existing:
                        raise ValueError("Stock-out record not found.")
                    cursor.execute("DELETE FROM stock_out WHERE stockout_id = %s", (stockout_id,))
                    cursor.execute(
                        "UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                        (existing["quantity_kg"], existing["product_id"]),
                    )
                conn.commit()
            self.refresh_stock_out()
            self.refresh_products()
            self._refresh_dropdowns()
            messagebox.showinfo("Success", f"{len(stockout_ids)} stock-out record(s) deleted.")
        except (ValueError, Error) as err:
            messagebox.showerror("Stock-Out Error", str(err))
    def add_sale_item(self):
        try:
            product_id = self._get_product_id_from_combo(self.sale_product)
            brand = self.sale_brand.get().strip()
            qty = self._to_decimal(self.sale_qty.get().strip(), "quantity")
            if not product_id:
                raise ValueError("Select product.")
            if not brand:
                raise ValueError("Select brand.")
            if qty <= 0:
                raise ValueError("Quantity must be greater than zero.")
            with db_cursor(dictionary=True) as (_, cursor):
                cursor.execute("SELECT product_name, unit_price, size FROM products WHERE product_id = %s", (product_id,))
                row = cursor.fetchone()
            if not row:
                raise ValueError("Product not found.")
            subtotal = row["unit_price"] * qty
            self.cart.append(
                {
                    "product_id": product_id,
                    "product_name": row["product_name"],
                    "brand": brand,
                    "size": row.get("size") if row else None,
                    "qty": qty,
                    "unit_price": row["unit_price"],
                    "subtotal": subtotal,
                }
            )
            self.sale_qty.set("")
            self._render_cart()
        except (ValueError, Error) as err:
            messagebox.showerror("Item Error", str(err))
    def _render_cart(self):
        self._clear_tree(self.cart_tree)
        total = Decimal("0.00")
        for idx, item in enumerate(self.cart):
            total += item["subtotal"]
            self.cart_tree.insert(
                "",
                "end",
                iid=idx,
                values=(
                    item["product_id"],
                    item["product_name"],
                    item.get("brand", ""),
                    item.get("size", "N/A"),
                    f"{item['qty']}",
                    f"{item['unit_price']}",
                    f"{item['subtotal']}",
                ),
            )
        self.total_var.set(f"Total: {total}")
    def clear_cart(self):
        self.cart = []
        self._render_cart()
    def _update_sale_brands(self, _event=None):
        """Update available brands for the selected product."""
        product_id = self._get_product_id_from_combo(self.sale_product)
        if not product_id:
            self.sale_brand["values"] = []
            return
        try:
            with db_cursor(dictionary=True) as (_, cursor):
                cursor.execute(
                    """
                    SELECT DISTINCT brand
                    FROM products
                    WHERE product_id = %s AND brand IS NOT NULL
                    ORDER BY brand ASC
                    """,
                    (product_id,),
                )
                rows = cursor.fetchall()
            brands = [r["brand"] for r in rows]
            self.sale_brand["values"] = brands
            if brands:
                self.sale_brand.set(brands[0])
            else:
                self.sale_brand.set("")
        except Error:
            self.sale_brand["values"] = []
            self.sale_brand.set("")
    def _delete_cart_item(self, _event=None):
        """Delete the selected cart item."""
        selected = self.cart_tree.selection()
        if selected:
            idx = int(selected[0])
            if 0 <= idx < len(self.cart):
                self.cart.pop(idx)
                self._render_cart()
    def _cart_right_click(self, event):
        """Right-click context menu for cart."""
        item = self.cart_tree.identify("item", event.x, event.y)
        if item:
            self.cart_tree.selection_set(item)
            menu = tk.Menu(self.cart_tree, tearoff=False)
            menu.add_command(label="Delete", command=lambda: self._delete_cart_item())
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.after_cancel(menu.after_id)
    def finalize_sale(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add sale items first.")
            return
        pay_method = self.sale_payment.get().strip()
        is_walkin = self.sale_walkin_var.get()
        customer_id = None if is_walkin else self._get_customer_id_from_combo(self.sale_customer)
        if is_walkin and pay_method != "Cash":
            messagebox.showwarning("Invalid Sale", "Walk-in customer sales must use cash payment.")
            return
        if pay_method == "Credit" and customer_id is None:
            messagebox.showwarning("Invalid Sale", "Credit sale requires a customer.")
            return
        total = sum((item["subtotal"] for item in self.cart), Decimal("0.00"))
        try:
            with db_cursor(dictionary=True) as (conn, cursor):
                for item in self.cart:
                    cursor.execute("SELECT stock_quantity FROM products WHERE product_id = %s", (item["product_id"],))
                    stock_row = cursor.fetchone()
                    if not stock_row:
                        raise ValueError(f"Product ID {item['product_id']} not found.")
                    if stock_row["stock_quantity"] < item["qty"]:
                        raise ValueError(f"Insufficient stock for {item['product_name']}.")
                sale_id = self._next_available_id(cursor, "sales", "sale_id")
                cursor.execute(
                    """
                    INSERT INTO sales (sale_id, employee_id, customer_id, total_amount, pay_method)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (sale_id, self.user["employee_id"], customer_id, total, pay_method),
                )
                for item in self.cart:
                    sale_item_id = self._next_available_id(cursor, "sale_items", "sale_item_id")
                    cursor.execute(
                        "INSERT INTO sale_items (sale_item_id, sale_id, product_id, quantity, subtotal) VALUES (%s, %s, %s, %s, %s)",
                        (sale_item_id, sale_id, item["product_id"], item["qty"], item["subtotal"]),
                    )
                conn.commit()
            self.clear_cart()
            self.sale_walkin_var.set(False)
            self.sale_payment.set("Cash")
            self.sale_customer.set("")
            self._sync_sale_customer_state()
            self.refresh_all()
            messagebox.showinfo("Success", "Sale saved successfully.")
        except (ValueError, Error) as err:
            messagebox.showerror("Sale Error", str(err))
    def delete_sale(self):
        if self.sales_history_tree is None or not self.sales_history_tree.winfo_exists():
            messagebox.showwarning("Sales History", "Open Sales History first.")
            return
        sale_ids = self._selected_ids(self.sales_history_tree)
        if not sale_ids:
            messagebox.showwarning("No Selection", "Select one or more sales from Sales History first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {len(sale_ids)} selected sale(s) and their items?"):
            return
        try:
            with db_cursor(dictionary=True) as (conn, cursor):
                for sale_id in sale_ids:
                    cursor.execute(
                        "SELECT customer_id, pay_method, total_amount FROM sales WHERE sale_id = %s",
                        (sale_id,),
                    )
                    sale_row = cursor.fetchone()
                    if not sale_row:
                        raise ValueError("Sale record not found.")
                    cursor.execute("SELECT product_id, quantity FROM sale_items WHERE sale_id = %s", (sale_id,))
                    sale_items = cursor.fetchall()
                    cursor.execute("DELETE FROM sale_items WHERE sale_id = %s", (sale_id,))
                    cursor.execute("DELETE FROM sales WHERE sale_id = %s", (sale_id,))
                    for item in sale_items:
                        cursor.execute(
                            "UPDATE products SET stock_quantity = stock_quantity + %s WHERE product_id = %s",
                            (item["quantity"], item["product_id"]),
                        )
                    if sale_row["pay_method"] == "Credit" and sale_row["customer_id"] is not None:
                        cursor.execute(
                            """
                            UPDATE customers
                            SET current_bal = current_bal - %s
                            WHERE customer_id = %s
                            """,
                            (sale_row["total_amount"], sale_row["customer_id"]),
                        )
                conn.commit()
            self.refresh_all()
            messagebox.showinfo("Success", f"{len(sale_ids)} sale(s) deleted.")
        except (ValueError, Error) as err:
            messagebox.showerror("Error", str(err))
    def view_selected_sale_record(self):
        if self.sales_history_tree is None or not self.sales_history_tree.winfo_exists():
            messagebox.showwarning("Sales History", "Open Sales History first.")
            return
        selected = self.sales_history_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a sale record first.")
            return
        sale_id = int(self.sales_history_tree.item(selected[0], "values")[0])
        try:
            with db_cursor(dictionary=True) as (_, cursor):
                cursor.execute(
                    f"""
                    SELECT
                        s.sale_id,
                        s.sale_date,
                        s.employee_id,
                        e.name AS employee_name,
                        COALESCE({QUALIFIED_CUSTOMER_NAME_SQL}, 'Walk-in Customer') AS customer_name,
                        s.pay_method,
                        s.total_amount
                    FROM sales s
                    JOIN employees e ON e.employee_id = s.employee_id
                    LEFT JOIN customers c ON c.customer_id = s.customer_id
                    WHERE s.sale_id = %s
                    """,
                    (sale_id,),
                )
                sale = cursor.fetchone()
                cursor.execute(
                    """
                    SELECT p.product_name, si.quantity, si.subtotal
                    FROM sale_items si
                    JOIN products p ON p.product_id = si.product_id
                    WHERE si.sale_id = %s
                    ORDER BY si.sale_item_id ASC
                    """,
                    (sale_id,),
                )
                items = cursor.fetchall()
            if not sale:
                raise ValueError("Sale record not found.")
            lines = [
                f"Sale ID: {sale['sale_id']}",
                f"Date: {sale['sale_date']}",
                f"Customer: {sale['customer_name']}",
                f"Employee ID: {sale['employee_id']}",
                f"Executed by: {sale['employee_name']}",
                f"Payment: {sale['pay_method']}",
                "",
                "Items:",
            ]
            if not items:
                lines.append(" - No sale items found.")
            else:
                for item in items:
                    lines.append(
                        f" - {item['product_name']} x{item['quantity']} = {item['subtotal']}"
                    )
            lines.append("")
            lines.append(f"Total: {sale['total_amount']}")
            messagebox.showinfo("Sale Record View", "\n".join(lines))
        except (ValueError, Error) as err:
            messagebox.showerror("Record View Error", str(err))
    def refresh_products(self):
        self._sync_product_stock_balances()
        rows = self._fetch_rows(
            """
            SELECT product_id, product_name, brand, size, unit_price, stock_quantity, reorder_point
            FROM products
            ORDER BY product_id
            """
        )
        self._populate_tree(
            self.products_tree,
            rows,
            lambda row: (
                row["product_id"],
                row["product_name"],
                row["brand"],
                row["size"],
                row["unit_price"],
                row["stock_quantity"],
            ),
        )
    def _sync_product_stock_balances(self):
        with db_cursor() as (conn, cursor):
            cursor.execute(
                """
                UPDATE products p
                LEFT JOIN (
                    SELECT product_id, COALESCE(SUM(quantity_kg), 0) AS total_stock_in
                    FROM stock_in
                    WHERE arrival_temp <= 5.0
                    GROUP BY product_id
                ) si ON si.product_id = p.product_id
                LEFT JOIN (
                    SELECT product_id, COALESCE(SUM(quantity_kg), 0) AS total_stock_out
                    FROM stock_out
                    GROUP BY product_id
                ) so ON so.product_id = p.product_id
                LEFT JOIN (
                    SELECT product_id, COALESCE(SUM(quantity), 0) AS total_sold
                    FROM sale_items
                    GROUP BY product_id
                ) sales ON sales.product_id = p.product_id
                SET p.stock_quantity = GREATEST(
                    COALESCE(si.total_stock_in, 0)
                    - COALESCE(so.total_stock_out, 0)
                    - COALESCE(sales.total_sold, 0),
                    0
                )
                """
            )
            conn.commit()
    def refresh_employees(self):
        rows = self._fetch_rows(
            "SELECT employee_id, name, username, role, date_hired FROM employees ORDER BY employee_id"
        )
        self._populate_tree(
            self.employees_tree,
            rows,
            lambda row: (
                row["employee_id"],
                row["name"],
                row["username"],
                row["role"],
                row["date_hired"] or "",
            ),
        )

    def refresh_customers(self):
        rows = self._fetch_rows(
            f"""
            SELECT
                customer_id,
                {CUSTOMER_NAME_SQL} AS customer_name,
                contact_num,
                current_bal AS balance
            FROM customers
            ORDER BY customer_id
            """
        )
        self._populate_tree(
            self.customers_tree,
            rows,
            lambda row: (
                row["customer_id"],
                row["customer_name"],
                row["contact_num"],
                row["balance"],
            ),
        )

    def refresh_suppliers(self):
        rows = self._fetch_rows(
            """
            SELECT supplier_id, supplier_name, contact, COALESCE(address, '') AS address
            FROM suppliers
            ORDER BY supplier_id
            """
        )
        self._populate_tree(
            self.suppliers_tree,
            rows,
            lambda row: (
                row["supplier_id"],
                row["supplier_name"],
                row["contact"],
                row["address"],
            ),
        )

    def refresh_stock_in(self):
        rows = self._fetch_rows(
            """
            SELECT
                v.stockin_id,
                v.product_name,
                v.supplier_name,
                e.name AS employee_name,
                v.quantity_kg,
                v.arrival_temp,
                v.safety_status,
                s.batch_id,
                v.date_received
            FROM vw_supplier_safety_audit v
            JOIN stock_in s ON s.stockin_id = v.stockin_id
            JOIN employees e ON e.employee_id = s.employee_id
            ORDER BY v.stockin_id ASC
            LIMIT 150
            """
        )
        self._populate_tree(
            self.stock_tree,
            rows,
            lambda row: (
                row["stockin_id"],
                row["product_name"],
                row["supplier_name"],
                row["employee_name"],
                row["quantity_kg"],
                row["arrival_temp"],
                row["safety_status"],
                row["batch_id"] or "",
                row["date_received"],
            ),
        )

    def refresh_stock_out(self):
        if self.stockout_tree is None:
            return
        rows = self._fetch_rows(
            """
            SELECT
                so.stockout_id,
                p.product_name,
                e.name AS employee_name,
                so.quantity_kg,
                so.reason,
                so.date_out
            FROM stock_out so
            JOIN products p ON p.product_id = so.product_id
            JOIN employees e ON e.employee_id = so.employee_id
            ORDER BY so.stockout_id ASC
            LIMIT 200
            """
        )
        self._populate_tree(
            self.stockout_tree,
            rows,
            lambda row: (
                row["stockout_id"],
                row["product_name"],
                row["employee_name"],
                row["quantity_kg"],
                row["reason"],
                row["date_out"],
            ),
        )

    def refresh_sales_history(self):
        if self.sales_history_tree is None or not self.sales_history_tree.winfo_exists():
            return
        rows = self._fetch_rows(
            f"""
            SELECT
                s.sale_id,
                s.sale_date,
                COALESCE({QUALIFIED_CUSTOMER_NAME_SQL}, 'Walk-in Customer') AS customer_name,
                s.employee_id,
                e.name AS employee_name,
                s.pay_method,
                s.total_amount,
                COALESCE(
                    GROUP_CONCAT(
                        CONCAT(p.product_name, ' x', si.quantity)
                        ORDER BY p.product_name SEPARATOR ', '
                    ),
                    'No items'
                ) AS items_added
            FROM sales s
            JOIN employees e ON e.employee_id = s.employee_id
            LEFT JOIN customers c ON c.customer_id = s.customer_id
            LEFT JOIN sale_items si ON si.sale_id = s.sale_id
            LEFT JOIN products p ON p.product_id = si.product_id
            GROUP BY
                s.sale_id,
                s.sale_date,
                c.is_business,
                c.business_name,
                c.first_name,
                c.middle_name,
                c.last_name,
                s.employee_id,
                e.name,
                s.pay_method,
                s.total_amount
            ORDER BY s.sale_id DESC
            LIMIT 150
            """
        )
        self._populate_tree(
            self.sales_history_tree,
            rows,
            lambda row: (
                row["sale_id"],
                row["sale_date"],
                row["customer_name"],
                row["employee_id"],
                row["employee_name"],
                row["pay_method"],
                row["items_added"],
                row["total_amount"],
            ),
        )
    def _get_browser_dataset(self, table_name):
        view_specs = {
            "vw_inventory_status": (VIEW_INVENTORY_STATUS, "status_priority ASC, stock_gap_kg ASC, product_name ASC"),
            "vw_detailed_sales": (VIEW_DETAILED_SALES, "transaction_id DESC"),
            "vw_supplier_safety_audit": (
                VIEW_SUPPLIER_SAFETY,
                "CASE action_level WHEN 'Critical' THEN 1 WHEN 'Review' THEN 2 ELSE 3 END ASC, temp_breach_c DESC, stockin_id DESC",
            ),
        }
        view, order = view_specs[table_name]
        with db_cursor() as (_, cursor):
            return fetch_view_rows(cursor, view, order, 250)
    def refresh_dashboard(self):
        if not hasattr(self, "dashboard_tab"):
            return
        try:
            dashboard = self._fetch_dashboard_data()
            activity = self._fetch_dashboard_activity()
        except Error as err:
            messagebox.showerror("Dashboard Error", str(err))
            return
        overview = dashboard["overview"]
        total_stock = Decimal(str(overview["total_stock_kg"] or 0))
        total_sales = Decimal(str(overview["total_sales_amount"] or 0))
        customer_balance = Decimal(str(overview["total_customer_balance"] or 0))
        self.dashboard_stat_vars["products"].set(str(overview["products_count"]))
        self.dashboard_stat_vars["stock"].set(f"{total_stock:.2f} kg")
        self.dashboard_stat_vars["sales"].set(f"{total_sales:.2f}")
        self.dashboard_stat_vars["alerts"].set(str(overview["low_stock_count"]))
        self.dashboard_stat_vars["products_meta"].set(f"{overview['customers_count']} customers on file")
        self.dashboard_stat_vars["stock_meta"].set(f"{overview['stockin_count']} stock-in records logged")
        self.dashboard_stat_vars["sales_meta"].set(f"{overview['sales_count']} sale(s) completed")
        self.dashboard_stat_vars["alerts_meta"].set(f"{overview['low_stock_count']} item(s) need attention")
        self.dashboard_date_var.set(date.today().strftime("%B %d, %Y"))
        self.dashboard_summary_var.set(
            "Quick view: {0} suppliers active, {1} sale items recorded, and {2:.2f} in total customer balance.".format(
                overview["suppliers_count"],
                overview["sale_items_count"],
                customer_balance,
            )
        )
        self.dashboard_focus_var.set(
            "Cash sales: {0} | Credit sales: {1} | Low or out-of-stock : {2}".format(
                dashboard["cash_count"],
                dashboard["credit_count"],
                overview["low_stock_count"],
            )
        )
        tree_specs = (
            (self.dashboard_sales_tree, activity["recent_sales"], ("customer_name", "total_amount"), self.dashboard_sales_hint_var, "No sales recorded yet."),
        )
        for tree, rows, keys, hint_var, empty_text in tree_specs:
            self._clear_tree(tree)
            if rows:
                hint_var.set(f"Showing the latest {len(rows)} record(s).")
                for row in rows:
                    tree.insert("", "end", values=tuple(row[key] for key in keys))
            else:
                hint_var.set(empty_text)
    def refresh_all(self):
        try:
            self.refresh_dashboard()
            self.refresh_products()
            self.refresh_employees()
            self.refresh_customers()
            self.refresh_suppliers()
            self.refresh_stock_in()
            self.refresh_stock_out()
            self.refresh_sales_history()
            self._refresh_dropdowns()
        except Error as err:
            messagebox.showerror("Database Error", str(err))
    def _pct_text(self, part, whole):
        try:
            part_val = float(part)
            whole_val = float(whole)
        except (TypeError, ValueError):
            return "0.00%"
        if whole_val == 0:
            return "0.00%"
        return f"{(part_val / whole_val) * 100:.2f}%"
    def _fetch_dashboard_data(self):
        with db_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM products) AS products_count,
                    (SELECT COUNT(*) FROM customers) AS customers_count,
                    (SELECT COUNT(*) FROM suppliers) AS suppliers_count,
                    (SELECT COUNT(*) FROM stock_in) AS stockin_count,
                    (SELECT COUNT(*) FROM sales) AS sales_count,
                    (SELECT COUNT(*) FROM sale_items) AS sale_items_count,
                    (SELECT COALESCE(SUM(stock_quantity), 0) FROM products) AS total_stock_kg,
                    (SELECT COALESCE(SUM(total_amount), 0) FROM sales) AS total_sales_amount,
                    (SELECT COALESCE(SUM(current_bal), 0) FROM customers) AS total_customer_balance,
                    (SELECT COUNT(*) FROM vw_inventory_status WHERE availability_status <> 'In Stock') AS low_stock_count
                """
            )
            overview = cursor.fetchone()
            cursor.execute("SELECT COUNT(*) AS cash_count FROM sales WHERE pay_method = 'Cash'")
            cash_count = cursor.fetchone()["cash_count"]
            cursor.execute("SELECT COUNT(*) AS credit_count FROM sales WHERE pay_method = 'Credit'")
            credit_count = cursor.fetchone()["credit_count"]
            cursor.execute(
                """
                SELECT p.product_name, COALESCE(SUM(si.quantity), 0) AS qty_sold
                FROM sale_items si
                JOIN products p ON p.product_id = si.product_id
                GROUP BY p.product_id, p.product_name
                ORDER BY qty_sold DESC
                LIMIT 5
                """
            )
            top_products = cursor.fetchall()
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) AS total_qty_sold FROM sale_items")
            total_qty_sold = cursor.fetchone()["total_qty_sold"]
            cursor.execute(
                """
                SELECT sp.supplier_name, COALESCE(SUM(s.quantity_kg), 0) AS qty_supplied
                FROM stock_in s
                JOIN suppliers sp ON sp.supplier_id = s.supplier_id
                GROUP BY sp.supplier_id, sp.supplier_name
                ORDER BY qty_supplied DESC
                LIMIT 5
                """
            )
            top_suppliers = cursor.fetchall()
            cursor.execute("SELECT COALESCE(SUM(quantity_kg), 0) AS total_stockin_qty FROM stock_in")
            total_stockin_qty = cursor.fetchone()["total_stockin_qty"]
            cursor.execute(
                """
                SELECT product_name, stock_quantity, availability_status AS status
                FROM vw_inventory_status
                WHERE availability_status <> 'In Stock'
                ORDER BY stock_quantity ASC, product_name ASC
                LIMIT 5
                """
            )
            low_stock_items = cursor.fetchall()
            cursor.execute(
                f"""
                SELECT
                    {CUSTOMER_NAME_SQL} AS customer_name,
                    current_bal AS balance,
                    CASE WHEN is_business = 1 THEN 'Business' ELSE 'Individual' END AS customer_type
                FROM customers
                WHERE current_bal > 0
                ORDER BY current_bal DESC, customer_id ASC
                LIMIT 5
                """
            )
            credit_watch = cursor.fetchall()
        return {
            "overview": overview,
            "cash_count": cash_count,
            "credit_count": credit_count,
            "top_products": top_products,
            "top_suppliers": top_suppliers,
            "total_qty_sold": total_qty_sold,
            "total_stockin_qty": total_stockin_qty,
            "low_stock_items": low_stock_items,
            "credit_watch": credit_watch,
        }
    def _fetch_dashboard_activity(self):
        with db_cursor(dictionary=True) as (_, cursor):
            cursor.execute(
                """
                SELECT
                    v.transaction_id AS sale_id,
                    MAX(v.customer_name) AS customer_name,
                    SUM(v.line_total) AS total_amount
                FROM vw_detailed_sales v
                GROUP BY v.transaction_id
                ORDER BY MAX(v.date_sold) DESC
                LIMIT 8
                """
            )
            recent_sales = cursor.fetchall()
        return {"recent_sales": recent_sales}


def main():
    app = PoultryCrudApp()
    app.mainloop()


if __name__ == "__main__":
    main()
