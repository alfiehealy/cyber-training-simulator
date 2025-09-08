
from __future__ import annotations
from collections import defaultdict, Counter
from typing import Dict, List, Tuple
from tkinter import Canvas
from models import RoundResult

def per_category(results: List[RoundResult], id_to_cat: Dict[str,str])->Dict[str,Tuple[int,int]]:
    acc: Dict[str,Tuple[int,int]] = defaultdict(lambda:(0,0))
    for r in results:
        cat = id_to_cat.get(r.scenario_id, "Other")
        correct = 1 if r.outcome=="Correct" else 0
        acc[cat] = (acc[cat][0]+correct, acc[cat][1]+1)
    return acc

def most_missed(results: List[RoundResult])->str:
    c = Counter(r.scenario_id for r in results if r.outcome=="Unsafe")
    return c.most_common(1)[0][0] if c else "None"

def draw_bar_chart(canvas: Canvas, data: Dict[str,Tuple[int,int]])->None:
    canvas.delete("all")
    if not data: return
    w = int(canvas["width"]); h = int(canvas["height"])
    margin, gap = 30, 12
    cats = list(data.keys())
    bar_w = max(20, (w-2*margin-gap*(len(cats)-1))//max(1,len(cats)))
    x = margin
    for cat in cats:
        correct, total = data[cat]
        frac = (correct/total) if total else 0
        bh = int(frac*(h-2*margin))
        canvas.create_rectangle(x, h-margin-bh, x+bar_w, h-margin, fill="#3b82f6")
        canvas.create_text(x+bar_w//2, h-margin-bh-12, text=f"{int(frac*100)}%", anchor="s")
        canvas.create_text(x+bar_w//2, h-margin+10, text=cat, anchor="n", angle=20)
        x += bar_w + gap
