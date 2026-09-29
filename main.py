"""Loopline Digital website - everything in one file.

Run locally:   pip install -r req.txt   then   python main.py
Open:          http://localhost:5000
Host online:   start command  gunicorn main:app
Contact-form requests are saved to leads.csv next to this file.
"""
import csv
import os
from datetime import datetime, timezone

from flask import Flask, Response, jsonify, request

BASE = os.path.dirname(os.path.abspath(__file__))
LEADS = os.path.join(BASE, "leads.csv")
app = Flask(__name__)

FAVICON = r"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Loopline Digital">
  <rect width="64" height="64" rx="16" fill="#2A4BFF"/>
  <circle cx="32" cy="32" r="19" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-dasharray="88 32" stroke-dashoffset="0"/>
  <polyline points="20,43 29,34 35,39 48,21" fill="none" stroke="#3DDBB0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <polyline points="39,20 48,20 48,29" fill="none" stroke="#3DDBB0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>"""

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Loopline Digital – Marketing that pays for itself</title>
<meta name="description" content="Loopline Digital runs SEO, paid ads, social and email for growing businesses, and reports on revenue, not vanity metrics.">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@500;700;800&family=DM+Sans:wght@400;500;700&display=swap">
<style>
:root{--bg:#F5F7FB;--surface:#fff;--ink:#101828;--mute:#5B6478;--line:#DDE2EE;--blue:#2A4BFF;--blue-ink:#fff;--mint:#12A67F;--sun:#FFC94A;--h:'Bricolage Grotesque',Georgia,serif;--b:'DM Sans',system-ui,sans-serif;
box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0D1220;--surface:#151C30;--ink:#EEF1FA;--mute:#9AA4BD;--line:#26304B;--blue:#6C86FF;--blue-ink:#0D1220;--mint:#3DDBB0}}
:root[data-theme="dark"]{--bg:#0D1220;--surface:#151C30;--ink:#EEF1FA;--mute:#9AA4BD;--line:#26304B;--blue:#6C86FF;--blue-ink:#0D1220;--mint:#3DDBB0}
html{scroll-padding-top:calc(env(safe-area-inset-top,0px) + 110px);scroll-behavior:smooth}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:400 17px/1.6 var(--b)}
h1,h2,h3{font-family:var(--h);line-height:1.08;margin:0;letter-spacing:-.02em}
h1{font-size:clamp(2.4rem,6vw,4.4rem);font-weight:800}
h2{font-size:clamp(1.8rem,3.6vw,2.7rem);font-weight:700}
h3{font-size:1.25rem;font-weight:700}
p{margin:0 0 1em;max-width:62ch}
a{color:inherit}
:focus-visible{outline:3px solid var(--blue);outline-offset:3px}
.wrap{max-width:1120px;margin:0 auto;padding:0 22px}
section{padding:84px 0}
header{position:sticky;top:env(safe-area-inset-top,0px);z-index:9;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
nav{display:flex;align-items:center;justify-content:space-between;gap:10px 16px;flex-wrap:wrap;min-height:64px;padding:8px 0}
.logo{font:800 1.25rem var(--h);text-decoration:none;display:flex;align-items:center;gap:8px}
.logo span{display:flex;flex-direction:column;line-height:1}.logo small{font:500 .62rem var(--b);letter-spacing:.14em;color:var(--mute);margin-top:3px;text-transform:uppercase}
nav ul{display:flex;gap:6px;list-style:none;margin:0;padding:0;font-size:.92rem}
nav ul a{display:block;text-decoration:none;color:var(--ink);padding:7px 15px;border-radius:999px;border:1.5px solid var(--line);white-space:nowrap;font-weight:500}
nav ul a:hover{border-color:var(--blue)}nav ul a.on,nav ul li:last-child a{background:var(--blue);border-color:var(--blue);color:var(--blue-ink)}
.posts{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.post{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:24px}.post small{color:var(--mute)}.post h3{margin:8px 0 10px}.post details{border:0;padding:0}.post summary{font:700 .95rem var(--b);color:var(--blue)}.post summary::after{content:''}.post details p{font-size:.95rem}
.about{display:grid;grid-template-columns:1.2fr .8fr;gap:48px;align-items:start}.stats{display:grid;grid-template-columns:1fr 1fr;gap:14px}.stats div{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:20px}.stats b{display:block;font:800 2rem var(--h);color:var(--blue)}.stats span{font-size:.9rem;color:var(--mute)}
.btn{display:inline-block;background:var(--blue);color:var(--blue-ink);font:700 1rem var(--b);padding:13px 22px;border-radius:10px;border:0;text-decoration:none;cursor:pointer}
.btn.alt{background:transparent;color:var(--ink);border:1.5px solid var(--line)}
.hero{padding:64px 0 80px}
.hero-grid{display:grid;grid-template-columns:1.05fr .95fr;gap:48px;align-items:center}
.hero p.lead{font-size:1.2rem;color:var(--mute);margin:22px 0 28px}
.cta{display:flex;gap:12px;flex-wrap:wrap}
.calc{background:var(--surface);border:1.5px solid var(--ink);border-radius:18px;padding:26px;box-shadow:8px 8px 0 var(--blue)}
.calc h3{margin-bottom:4px}.calc small{color:var(--mute)}
label{display:block;font-weight:700;font-size:.92rem;margin:18px 0 6px}
label output{float:right;color:var(--blue)}
input[type=range]{width:100%;accent-color:var(--blue)}
select,input[type=text],input[type=email],textarea{width:100%;font:inherit;padding:11px 12px;border:1.5px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink)}
.res{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:22px;padding-top:18px;border-top:1px dashed var(--line)}
.res b{display:block;font:800 1.6rem var(--h);color:var(--mint)}.res span{font-size:.8rem;color:var(--mute)}
.logos{border-block:1px solid var(--line);padding:22px 0;color:var(--mute);font-size:.95rem}
.logos .wrap{display:flex;gap:28px;flex-wrap:wrap;justify-content:space-between;align-items:center}
.logos strong{font-family:var(--h);font-size:1.1rem;color:var(--ink)}
.head{margin-bottom:40px}.head p{color:var(--mute);margin-top:14px}
.svc{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.svc article{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:26px}
.svc article:first-child{grid-column:span 2;background:var(--blue);color:var(--blue-ink);border-color:var(--blue)}
.svc article:first-child p{color:inherit;opacity:.9}
.svc p{color:var(--mute);margin:10px 0 14px}.svc ul{margin:0;padding-left:18px;font-size:.95rem}
.steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:0;counter-reset:s}
.steps li{counter-increment:s;padding:0 22px 0 0;border-top:3px solid var(--ink);padding-top:18px}
.steps li::before{content:counter(s);display:inline-grid;place-items:center;width:32px;height:32px;border-radius:50%;background:var(--sun);color:#101828;font:800 .95rem var(--h);margin-bottom:12px}
.steps p{color:var(--mute);font-size:.95rem;margin-top:6px}
.band{background:var(--ink);color:var(--bg)}
.band .head p{color:color-mix(in srgb,var(--bg) 70%,transparent)}
.cases{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.case{border:1px solid color-mix(in srgb,var(--bg) 25%,transparent);border-radius:14px;padding:26px}
.case b{display:block;font:800 2.6rem/1 var(--h);color:var(--sun);margin-bottom:10px}
.case p{margin:0;font-size:.95rem;opacity:.85}
.case cite{display:block;margin-top:14px;font-size:.85rem;opacity:.65;font-style:normal}
.price{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;align-items:stretch}
.plan{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:28px;display:flex;flex-direction:column}
.plan.pop{border:2px solid var(--blue)}
.plan .amt{font:800 2.2rem var(--h);margin:8px 0}.plan .amt small{font:400 .95rem var(--b);color:var(--mute)}
.plan ul{padding-left:18px;margin:12px 0 22px;color:var(--mute);flex:1}
.faq{max-width:780px}
details{border-bottom:1px solid var(--line);padding:18px 0}
summary{font:700 1.1rem var(--h);cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:12px}
summary::after{content:"+";color:var(--blue);font-size:1.4rem;line-height:1}
details[open] summary::after{content:"–"}
details p{color:var(--mute);margin:12px 0 0}
.contact{display:grid;grid-template-columns:1fr 1fr;gap:48px}
form{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:26px}
form .btn{margin-top:18px;width:100%}
#msg{margin-top:12px;color:var(--mint);font-weight:700;min-height:1.4em}
footer{border-top:1px solid var(--line);padding:30px 0;color:var(--mute);font-size:.9rem}
footer .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
@media(max-width:900px){.hero-grid,.contact,.svc,.cases,.price,.posts,.about{grid-template-columns:1fr}nav ul{width:100%;overflow-x:auto;padding-bottom:4px}.svc article:first-child{grid-column:auto}.steps{grid-template-columns:1fr 1fr;gap:28px 0}section{padding:60px 0}}
@media(max-width:520px){.steps{grid-template-columns:1fr}.res{grid-template-columns:1fr 1fr 1fr;gap:6px}.res b{font-size:1.25rem}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style>
</head>
<body>
<header><div class="wrap"><nav aria-label="Main">
<a class="logo" href="#top" aria-label="Loopline Digital, home"><svg width="34" height="34" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="16" fill="#2A4BFF"/><circle cx="32" cy="32" r="19" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-dasharray="88 32"/><polyline points="20,43 29,34 35,39 48,21" fill="none" stroke="#3DDBB0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><polyline points="39,20 48,20 48,29" fill="none" stroke="#3DDBB0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Loopline<small>Digital marketing</small></span></a>
<ul><li><a href="#top">Home</a></li><li><a href="#services">Services</a></li><li><a href="#blog">Blog</a></li><li><a href="#about">About us</a></li><li><a href="#contact">Contact</a></li></ul></nav></div></header>

<main id="top">
<section class="hero"><div class="wrap hero-grid">
<div>
<h1>Marketing you can trace to revenue.</h1>
<p class="lead">Loopline runs SEO, paid ads, social and email for small and mid-sized businesses. Every report shows leads, sales and cost, not likes and impressions.</p>
<div class="cta"><a class="btn" href="#contact">Book a free audit</a><a class="btn alt" href="#results">See client results</a></div>
</div>
<div class="calc" role="group" aria-labelledby="ct">
<h3 id="ct">What could your budget return?</h3><small>A quick estimate based on typical results.</small>
<label for="ch">Main channel</label>
<select id="ch"><option value="28">Google Search ads</option><option value="22">Social ads</option><option value="14">SEO and content</option><option value="9">Email and automation</option></select>
<label for="bd">Monthly budget <output id="bo">$3,000</output></label>
<input id="bd" type="range" min="500" max="20000" step="250" value="3000">
<label for="sv">Average sale value <output id="so">$400</output></label>
<input id="sv" type="range" min="50" max="5000" step="50" value="400">
<div class="res" aria-live="polite"><div><b id="r1">0</b><span>leads / month</span></div><div><b id="r2">0</b><span>new customers</span></div><div><b id="r3">0</b><span>return per $1</span></div></div>
</div></div></section>

<div class="logos"><div class="wrap"><strong>Trusted by 120+ local and online businesses</strong><span>Dental clinics</span><span>Online stores</span><span>Law firms</span><span>Restaurants</span><span>SaaS teams</span></div></div>

<section id="services"><div class="wrap">
<div class="head"><h2>Everything that brings customers in</h2><p>Pick one service or let us run the whole funnel. Each one comes with a named specialist and a monthly report.</p></div>
<div class="svc">
<article><h3>Search engine optimization</h3><p>Show up when people search for what you sell. We fix technical issues, write content that answers real questions, and build links from sites your customers trust.</p><ul><li>Site and keyword audit</li><li>Local SEO and Google Business Profile</li><li>Blog and landing page content</li></ul></article>
<article><h3>Paid advertising</h3><p>Google, Meta, LinkedIn and YouTube campaigns with tracking set up before the first rupee or dollar is spent.</p><ul><li>Campaign setup and testing</li><li>Weekly budget checks</li></ul></article>
<article><h3>Social media</h3><p>A steady posting plan, short video and community replies in your brand's voice.</p><ul><li>Content calendar</li><li>Reels and short video</li></ul></article>
<article><h3>Email and WhatsApp</h3><p>Welcome series, cart reminders and win-back messages that run on their own.</p><ul><li>Automation flows</li><li>List cleaning</li></ul></article>
<article><h3>Website and conversion</h3><p>Faster pages, clearer offers and forms that get filled in. We test one change at a time.</p><ul><li>Landing pages</li><li>A/B testing</li></ul></article>
</div></div></section>

<section id="process" style="background:var(--surface);border-block:1px solid var(--line)"><div class="wrap">
<div class="head"><h2>How we work</h2><p>Four steps, repeated every month. You always know what is being tested and why.</p></div>
<ol class="steps">
<li><h3>Audit</h3><p>We review your site, ads, analytics and competitors, then send a written plan within 5 working days.</p></li>
<li><h3>Set up</h3><p>Tracking, accounts and first campaigns go live. Every lead and call is tagged to its source.</p></li>
<li><h3>Run and test</h3><p>We change one thing at a time, keep what works and drop what does not.</p></li>
<li><h3>Report</h3><p>A one-page monthly report shows spend, leads, sales and next steps. A call follows.</p></li>
</ol></div></section>

<section id="results" class="band"><div class="wrap">
<div class="head"><h2>Results our clients see</h2><p>Figures are from the first 6 months of each engagement.</p></div>
<div class="cases">
<div class="case"><b>3.4×</b><p>Return on ad spend for an online homeware store after we rebuilt its Google Shopping campaigns.</p><cite>E-commerce client</cite></div>
<div class="case"><b>+212%</b><p>Organic enquiries for a dental clinic group after local SEO and review requests.</p><cite>Healthcare client</cite></div>
<div class="case"><b>−38%</b><p>Cost per lead for a B2B software firm after landing page tests and LinkedIn targeting fixes.</p><cite>SaaS client</cite></div>
</div></div></section>

<section id="pricing"><div class="wrap">
<div class="head"><h2>Simple monthly plans</h2><p>No long contracts. Cancel with 30 days' notice. Ad spend is paid to the platforms directly.</p></div>
<div class="price">
<div class="plan"><h3>Starter</h3><div class="amt">$490<small> / month</small></div><ul><li>One channel</li><li>Monthly report</li><li>Email support</li></ul><a class="btn alt" href="#contact">Choose Starter</a></div>
<div class="plan pop"><h3>Growth</h3><div class="amt">$1,290<small> / month</small></div><ul><li>Up to three channels</li><li>Conversion testing</li><li>Fortnightly calls</li></ul><a class="btn" href="#contact">Choose Growth</a></div>
<div class="plan"><h3>Full funnel</h3><div class="amt">Custom</div><ul><li>All channels</li><li>Dedicated strategist</li><li>Weekly dashboard</li></ul><a class="btn alt" href="#contact">Talk to us</a></div>
</div></div></section>

<section id="blog"><div class="wrap">
<div class="head"><h2>Blog</h2><p>Practical marketing advice, written for business owners.</p></div>
<div class="posts">
<article class="post"><small>SEO · 5 min read</small><h3>5 SEO fixes you can make this week</h3><details><summary>Read more</summary><p>Start with page titles that match what people search, compress heavy images, fix broken links, claim your Google Business Profile and add your city to key pages. These five changes take a few hours and often lift enquiries within weeks.</p></details></article>
<article class="post"><small>Ads · 4 min read</small><h3>How much should a small business spend on ads?</h3><details><summary>Read more</summary><p>Work backwards from your goal. If a customer is worth $400 and you can pay $80 to win one, and about 1 in 8 leads buys, you can pay up to $10 per lead. Start small, test for 4 weeks, then raise spend on what works.</p></details></article>
<article class="post"><small>Email · 3 min read</small><h3>Email flows that earn while you sleep</h3><details><summary>Read more</summary><p>Three automations pay off fastest: a welcome series for new subscribers, a reminder for abandoned carts, and a win-back message for customers who have gone quiet for 90 days.</p></details></article>
</div></div></section>

<section id="about" style="background:var(--surface);border-block:1px solid var(--line)"><div class="wrap about">
<div><h2>About us</h2><p style="margin-top:16px">Loopline started in 2020 with one idea: marketing should be judged by the sales it brings, not by the reports it fills.</p><p>We are a small team of SEO, ads and email specialists. You talk to the people doing the work, and every plan starts with your numbers.</p><p><strong>What we promise:</strong> clear reports, no lock-in contracts, and you always own your accounts and data.</p><a class="btn" href="#contact">Work with us</a></div>
<div class="stats"><div><b>120+</b><span>clients served</span></div><div><b>6 yrs</b><span>in business</span></div><div><b>12</b><span>specialists</span></div><div><b>30 days</b><span>notice to cancel</span></div></div>
</div></section>

<section id="faq" style="padding-top:0"><div class="wrap">
<div class="head"><h2>Questions we hear a lot</h2></div>
<div class="faq">
<details><summary>How soon will I see results?</summary><p>Paid ads can bring leads in the first two weeks. SEO usually takes 3 to 6 months to build steady growth.</p></details>
<details><summary>Do I need a big budget?</summary><p>No. Many clients start with $500 to $1,500 a month in ad spend and grow once the numbers work.</p></details>
<details><summary>Who owns the ad accounts?</summary><p>You do. We are added as managers, so you can leave at any time and keep your data.</p></details>
<details><summary>How do you measure success?</summary><p>By leads, sales and cost per customer. We set these goals with you in the audit.</p></details>
</div></div></section>

<section id="contact" style="background:var(--surface);border-top:1px solid var(--line)"><div class="wrap contact">
<div><h2>Get your free marketing audit</h2><p style="margin-top:16px;color:var(--mute)">Tell us about your business. We reply within one working day with a short review of what to fix first.</p><p><strong>Email:</strong> hello@looplinedigital.example<br><strong>Hours:</strong> Mon–Sat, 9:30 am – 6:30 pm IST</p></div>
<form id="f" novalidate>
<label for="n" style="margin-top:0">Your name</label><input id="n" type="text" required autocomplete="name">
<label for="e">Work email</label><input id="e" type="email" required autocomplete="email">
<label for="w">Website (optional)</label><input id="w" type="text" placeholder="yourbusiness.com">
<label for="m">What do you want to improve?</label><textarea id="m" rows="4"></textarea>
<button class="btn" type="submit">Send my request</button><div id="msg" role="status"></div>
</form></div></section>
</main>

<footer><div class="wrap"><span>© 2026 Loopline Digital. All rights reserved.</span><span>SEO · Ads · Social · Email</span></div></footer>

<script>
(function(){
var $=function(i){return document.getElementById(i)};
var f=new Intl.NumberFormat('en-US');
function calc(){
var cpl=+$('ch').value,b=+$('bd').value,s=+$('sv').value;
$('bo').textContent='$'+f.format(b);$('so').textContent='$'+f.format(s);
var leads=Math.round(b/cpl),cust=Math.max(1,Math.round(leads*.12)),roas=(cust*s)/b;
$('r1').textContent=f.format(leads);$('r2').textContent=f.format(cust);$('r3').textContent='$'+roas.toFixed(1);
}
['ch','bd','sv'].forEach(function(i){$(i).addEventListener('input',calc)});calc();
$('f').addEventListener('submit',function(e){
e.preventDefault();
var n=$('n').value.trim(),em=$('e').value.trim(),m=$('msg');
if(!n||!/^\S+@\S+\.\S+$/.test(em)){m.style.color='#D92D20';m.textContent='Enter your name and a valid email address.';return}
m.style.color='';m.textContent='Sending…';
var body='Name: '+n+'\nEmail: '+em+'\nWebsite: '+$('w').value+'\n\n'+$('m').value;
fetch('/api/contact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,email:em,website:$('w').value,message:$('m').value})})
.then(function(x){if(!x.ok)throw 0;m.textContent='Thanks, '+n+'. We will reply within one working day.';$('f').reset()})
.catch(function(){window.location.href='mailto:hello@looplinedigital.example?subject='+encodeURIComponent('Free audit request from '+n)+'&body='+encodeURIComponent(body);m.textContent='Your email app should open with the request ready to send.'});
});
})();
</script>
</body>
</html>
"""


@app.get("/")
def home():
    return Response(PAGE, mimetype="text/html")


@app.get("/favicon.svg")
def favicon():
    return Response(FAVICON, mimetype="image/svg+xml")


@app.post("/api/contact")
def contact():
    d = request.get_json(silent=True) or {}
    name = str(d.get("name", "")).strip()[:120]
    email = str(d.get("email", "")).strip()[:160]
    if not name or "@" not in email:
        return jsonify(error="Name and valid email are required"), 400
    new = not os.path.exists(LEADS)
    with open(LEADS, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time_utc", "name", "email", "website", "message"])
        w.writerow([
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
            name, email,
            str(d.get("website", ""))[:200],
            str(d.get("message", ""))[:2000],
        ])
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
