from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, String, Integer, DateTime, Text, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)
engine = create_engine(f"sqlite:///{DATA / 'erp.db'}", connect_args={"check_same_thread": False})
Session = sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase): pass
class Party(Base):
    __tablename__ = "parties"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    kind: Mapped[str] = mapped_column(String(20))
    phone: Mapped[str] = mapped_column(String(50), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(40), unique=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("parties.id"))
    description: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    agreed_price_piasters: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="جديد")
    due_date: Mapped[str] = mapped_column(String(20), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True)
    name: Mapped[str] = mapped_column(String(180))
    unit: Mapped[str] = mapped_column(String(30), default="قطعة")
    qty_milli: Mapped[int] = mapped_column(Integer, default=0)
class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    action: Mapped[str] = mapped_column(String(100))
    details: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
app = FastAPI(title="Advertising & Print ERP Pilot")

def layout(body: str) -> str:
    return f"""<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>إدارة المطبعة</title><style>
body{{font-family:Tahoma,Arial;background:#f3f5f8;color:#182230;margin:0}}header{{background:#14283f;color:white;padding:22px 5vw}}
main{{max-width:1100px;margin:24px auto;padding:0 16px}}nav{{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}}
a,button{{background:#176b87;color:white;padding:10px 15px;border:0;border-radius:7px;text-decoration:none;cursor:pointer}}
.card{{background:white;border:1px solid #dce2e8;border-radius:12px;padding:18px;margin:14px 0;box-shadow:0 2px 8px #14283f0b}}
input,select,textarea{{padding:10px;border:1px solid #cbd5df;border-radius:6px;margin:5px;max-width:100%}}
table{{width:100%;border-collapse:collapse;background:white}}td,th{{padding:10px;border-bottom:1px solid #e5eaf0;text-align:right}}
small{{color:#64748b}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}
</style><header><h1>نظام إدارة الدعاية والمطبعة</h1><div>الإصدار التجريبي — وضع جهاز واحد</div></header><main>
<nav><a href="/">الرئيسية</a><a href="/parties">العملاء والموردون</a><a href="/jobs">أوامر الشغل</a><a href="/items">الأصناف والمخزون</a><a href="/events">سجل العمليات</a></nav>{body}
<footer><small>نسخة تطوير أولية — لا تستخدم للأرصدة أو القيود المالية الحقيقية قبل استكمال التحقق.</small></footer></main></html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    with Session() as s:
        parties=s.query(Party).count(); jobs=s.query(Job).count(); items=s.query(Item).count()
    return layout(f"""<div class="grid"><div class="card"><h2>{parties}</h2>الأطراف المسجلة</div><div class="card"><h2>{jobs}</h2>أوامر الشغل</div><div class="card"><h2>{items}</h2>الأصناف</div></div>
<div class="card"><h2>مركز التشغيل</h2><p>ابدأ بإضافة العملاء والموردين ثم سجّل أوامر الشغل والأصناف. سيتم توسيع النظام بدورة المستندات والترحيل المحاسبي بعد اختبار هذا الأساس.</p></div>""")

@app.get("/parties", response_class=HTMLResponse)
def parties():
    with Session() as s:
        rows=s.scalars(select(Party).order_by(Party.id.desc())).all()
    trs="".join(f"<tr><td>{p.id}</td><td>{p.name}</td><td>{p.kind}</td><td>{p.phone}</td></tr>" for p in rows)
    return layout(f"""<div class="card"><h2>إضافة طرف</h2><form method="post" action="/parties">
<input name="name" placeholder="الاسم" required><select name="kind"><option>عميل</option><option>مورد</option><option>شريك</option></select><input name="phone" placeholder="الهاتف"><input name="notes" placeholder="ملاحظات"><button>حفظ</button></form></div>
<div class="card"><h2>دليل الأطراف</h2><table><tr><th>#</th><th>الاسم</th><th>النوع</th><th>الهاتف</th></tr>{trs}</table></div>""")
@app.post("/parties")
def add_party(name:str=Form(...),kind:str=Form(...),phone:str=Form(""),notes:str=Form("")):
    if kind not in {"عميل","مورد","شريك"}: raise HTTPException(400,"نوع غير صالح")
    with Session() as s:
        p=Party(name=name.strip(),kind=kind,phone=phone.strip(),notes=notes.strip());s.add(p);s.flush()
        s.add(Event(action="إضافة طرف",details=f"{p.id}:{p.name}"));s.commit()
    return RedirectResponse("/parties",status_code=303)

@app.get("/jobs", response_class=HTMLResponse)
def jobs():
    with Session() as s:
        customers=s.scalars(select(Party).where(Party.kind=="عميل").order_by(Party.name)).all()
        rows=s.scalars(select(Job).order_by(Job.id.desc())).all()
    opts="".join(f'<option value="{p.id}">{p.name}</option>' for p in customers)
    trs="".join(f"<tr><td>{j.number}</td><td>{j.description}</td><td>{j.quantity}</td><td>{j.agreed_price_piasters/100:.2f} ج.م</td><td>{j.status}</td></tr>" for j in rows)
    return layout(f"""<div class="card"><h2>أمر شغل جديد</h2><form method="post" action="/jobs">
<input name="number" placeholder="رقم الأمر" required><select name="customer_id" required>{opts}</select><input name="description" placeholder="وصف العمل" required><input name="quantity" type="number" min="1" value="1"><input name="price" type="number" min="0" step=".01" placeholder="السعر بالجنيه"><input name="due_date" type="date"><button>حفظ الأمر</button></form></div>
<div class="card"><h2>أوامر الشغل</h2><table><tr><th>الرقم</th><th>الوصف</th><th>الكمية</th><th>السعر</th><th>الحالة</th></tr>{trs}</table></div>""")
@app.post("/jobs")
def add_job(number:str=Form(...),customer_id:int=Form(...),description:str=Form(...),quantity:int=Form(1),price:float=Form(0),due_date:str=Form("")):
    if quantity<1 or price<0: raise HTTPException(400,"الكمية والسعر غير صالحين")
    with Session() as s:
        if not s.get(Party,customer_id): raise HTTPException(400,"العميل غير موجود")
        if s.scalar(select(Job).where(Job.number==number)): raise HTTPException(409,"رقم أمر الشغل مستخدم")
        j=Job(number=number.strip(),customer_id=customer_id,description=description.strip(),quantity=quantity,agreed_price_piasters=round(price*100),due_date=due_date)
        s.add(j);s.add(Event(action="إنشاء أمر شغل",details=number));s.commit()
    return RedirectResponse("/jobs",status_code=303)

@app.get("/items",response_class=HTMLResponse)
def items():
    with Session() as s: rows=s.scalars(select(Item).order_by(Item.id.desc())).all()
    trs="".join(f"<tr><td>{i.code}</td><td>{i.name}</td><td>{i.unit}</td><td>{i.qty_milli/1000:g}</td></tr>" for i in rows)
    return layout(f"""<div class="card"><h2>إضافة صنف</h2><form method="post" action="/items"><input name="code" placeholder="كود الصنف" required><input name="name" placeholder="اسم الصنف" required><input name="unit" placeholder="الوحدة" value="قطعة"><button>حفظ</button></form></div><div class="card"><h2>الأصناف</h2><table><tr><th>الكود</th><th>الصنف</th><th>الوحدة</th><th>الرصيد</th></tr>{trs}</table></div>""")
@app.post("/items")
def add_item(code:str=Form(...),name:str=Form(...),unit:str=Form("قطعة")):
    with Session() as s:
        if s.scalar(select(Item).where(Item.code==code)): raise HTTPException(409,"الكود مستخدم")
        s.add(Item(code=code.strip(),name=name.strip(),unit=unit.strip()));s.add(Event(action="إضافة صنف",details=code));s.commit()
    return RedirectResponse("/items",status_code=303)

@app.get("/events",response_class=HTMLResponse)
def events():
    with Session() as s: rows=s.scalars(select(Event).order_by(Event.id.desc()).limit(200)).all()
    trs="".join(f"<tr><td>{e.created_at:%Y-%m-%d %H:%M}</td><td>{e.action}</td><td>{e.details}</td></tr>" for e in rows)
    return layout(f"<div class='card'><h2>آخر 200 عملية</h2><table><tr><th>التاريخ</th><th>العملية</th><th>التفاصيل</th></tr>{trs}</table></div>")

@app.get("/health")
def health(): return {"status":"ok","mode":"single-device-pilot"}
