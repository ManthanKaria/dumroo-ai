# utils.py
import pandas as pd
from typing import Dict, Optional

DATA_PATH = "data/students.csv"

def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["last_submission_date", "quiz_date"], dayfirst=False)
    return df

class AdminContext:
    """
    Represents the admin's scope. Example:
    AdminContext(role='admin', allowed_grade='8', allowed_class='A', allowed_region='North')
    """
    def __init__(self, admin_id: str, allowed_grade: Optional[str]=None, allowed_class: Optional[str]=None, allowed_region: Optional[str]=None):
        self.admin_id = admin_id
        self.allowed_grade = allowed_grade
        self.allowed_class = allowed_class
        self.allowed_region = allowed_region

    def __repr__(self):
        return f"AdminContext(admin_id={self.admin_id}, grade={self.allowed_grade}, class={self.allowed_class}, region={self.allowed_region})"

def apply_scope_filter(df: pd.DataFrame, ctx: AdminContext) -> pd.DataFrame:
    filtered = df.copy()
    if ctx.allowed_grade:
        filtered = filtered[filtered["grade"].astype(str) == str(ctx.allowed_grade)]
    if ctx.allowed_class:
        filtered = filtered[filtered["class"].astype(str).str.upper() == str(ctx.allowed_class).upper()]
    if ctx.allowed_region:
        filtered = filtered[filtered["region"].astype(str).str.lower() == str(ctx.allowed_region).lower()]
    return filtered
