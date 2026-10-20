import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from document_reader import extract_text
from speech import make_audio

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=False)

st.set_page_config(
    page_title="NammaSeve — Understand every notice",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# NammaSeve's visual system: Karnataka ivory, espresso, kumkum red and turmeric gold.
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&family=Noto+Sans+Kannada:wght@400;500;600;700&family=Noto+Serif+Kannada:wght@500;600;700&family=Noto+Sans+Telugu:wght@400;500;600;700&display=swap');
:root{--paper:#F6EEDA;--ink:#241711;--bronze:#946536;--gold:#D99A1E;--kum:#A4231B;--maroon:#5B140F;--card:#FFFEFA;--muted:#74695c;--line:#e0d0ae;--pale:#e8dcc2;--ease:cubic-bezier(.22,.8,.2,1)}
html,body,[class*="css"]{font-family:'DM Sans','Noto Sans Kannada','Noto Sans Telugu',sans-serif;color:var(--ink)}
html{scroll-behavior:smooth}
::selection{background:rgba(217,154,30,.35)}
.stApp{background:var(--paper);color:var(--ink)}
[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:transparent}
[data-testid="stHeader"]{background:transparent;backdrop-filter:none}
[data-testid="stToolbar"]{right:1rem}
.block-container{position:relative;z-index:1;max-width:1240px;padding-top:1.1rem;padding-bottom:4rem}
#MainMenu,footer{visibility:hidden}
header[data-testid="stHeader"]{height:2.6rem}
[data-stale="true"]{opacity:1!important;transition:none!important}
.element-container:has([data-testid="stMarkdownContainer"]:empty){display:none}
h1,h2,h3{color:var(--ink)!important;letter-spacing:-.035em}
h1,h2{font-family:'Playfair Display',Georgia,serif!important;font-weight:600!important}
h1{font-size:clamp(2.2rem,4vw,3.7rem)!important;line-height:1.08!important}
h2{font-size:clamp(1.65rem,2.6vw,2.35rem)!important}
p,li,label,.stMarkdown{color:var(--ink)}

/* ---------- 3D living background ---------- */
.world{position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none;background:radial-gradient(60vw 50vh at 88% 6%,rgba(255,196,96,.42),transparent 70%),radial-gradient(70vw 60vh at 2% 96%,rgba(164,35,27,.11),transparent 70%),linear-gradient(180deg,#FBF5E5 0%,#F6EEDA 52%,#EBDAB2 100%)}
.world>*{position:absolute}
.world .mandala{right:-17vmax;top:-17vmax;width:54vmax;height:54vmax;border-radius:50%;background:repeating-conic-gradient(from 0deg,rgba(164,35,27,.17) 0 1.2deg,transparent 1.2deg 11.25deg),repeating-radial-gradient(circle,rgba(148,101,54,.24) 0 1.5px,transparent 1.5px 4.4vmax);-webkit-mask-image:radial-gradient(circle,#000 22%,transparent 70%);mask-image:radial-gradient(circle,#000 22%,transparent 70%);animation:spinM 140s linear infinite;will-change:transform}
.world .floor{left:0;right:0;bottom:-6vh;height:56vh;perspective:1400px;perspective-origin:50% 0}
.world .plane{left:50%;top:calc(45% - 40vmax);width:80vmax;height:80vmax;margin-left:-40vmax;border-radius:50%;background:repeating-conic-gradient(from 0deg,rgba(148,101,54,.28) 0 .5deg,transparent .5deg 6deg),repeating-radial-gradient(circle,rgba(164,35,27,.22) 0 3px,transparent 3px 6vmax),radial-gradient(circle,rgba(217,154,30,.3),transparent 55%);-webkit-mask-image:radial-gradient(circle closest-side,#000 30%,transparent 100%);mask-image:radial-gradient(circle closest-side,#000 30%,transparent 100%);transform:rotateX(72deg);animation:spinF 170s linear infinite;will-change:transform}
.world .plane.p2{width:46vmax;height:46vmax;margin-left:-23vmax;top:calc(45% - 23vmax);opacity:.9;animation-direction:reverse;animation-duration:120s}
.world .orb{border-radius:50%;background:radial-gradient(circle at 32% 28%,rgba(255,255,255,.95),rgba(255,222,150,.6) 32%,rgba(217,154,30,.2) 66%,transparent 70%);box-shadow:0 30px 50px -20px rgba(120,70,10,.25);animation:floaty 14s ease-in-out infinite;will-change:transform}
.world .o1{width:13vmax;height:13vmax;left:-3vmax;top:22vh}
.world .o2{width:7vmax;height:7vmax;right:8vw;top:44vh;animation-duration:11s;animation-delay:-4s}
.world .o3{width:4.5vmax;height:4.5vmax;left:38vw;top:12vh;animation-duration:17s;animation-delay:-8s;opacity:.8}
.world .petals{left:0;right:0;top:0;height:calc(100% + 840px);opacity:.85;background:radial-gradient(circle,rgba(232,163,23,.7) 0 2.6px,transparent 3.6px) 40px 60px/420px 420px,radial-gradient(circle,rgba(164,35,27,.42) 0 2px,transparent 3px) 260px 230px/420px 420px,radial-gradient(circle,rgba(255,214,120,.9) 0 1.7px,transparent 2.7px) 120px 20px/280px 280px,radial-gradient(circle,rgba(217,154,30,.5) 0 2.2px,transparent 3.2px) 20px 190px/280px 280px,radial-gradient(circle,rgba(164,35,27,.3) 0 1.6px,transparent 2.6px) 150px 90px/210px 210px,radial-gradient(circle,rgba(255,236,180,.95) 0 1.5px,transparent 2.5px) 60px 150px/210px 210px;animation:rise 70s linear infinite;will-change:transform}
.world .grain{inset:0;opacity:.5;mix-blend-mode:multiply;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2'/%3E%3CfeColorMatrix values='0 0 0 0 .4 0 0 0 0 .28 0 0 0 0 .15 0 0 0 .2 0'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)'/%3E%3C/svg%3E")}

/* ---------- page transition veils ---------- */
.veil{position:fixed;inset:0;z-index:99999;pointer-events:none;display:flex}
.veil.curtain i{display:block;flex:1;background:repeating-linear-gradient(90deg,rgba(0,0,0,.16) 0 2px,transparent 2px 24px),linear-gradient(180deg,#7d1c14,#3a0d09);animation:curOpen 1.15s cubic-bezier(.77,0,.18,1) .2s both}
.veil.curtain i:first-child{border-right:6px solid var(--gold);--x:-103%}
.veil.curtain i:nth-child(2){border-left:6px solid var(--gold);--x:103%}
.veil.curtain b{position:absolute;left:50%;top:50%;font:700 5.5rem 'Noto Serif Kannada',serif;color:var(--gold);text-shadow:0 0 40px rgba(255,190,70,.6);animation:emblem 1.1s ease both}
.veil.soft{background:linear-gradient(120deg,#F6EEDA,#fbe9c6);animation:veilOut .9s ease .05s both}

/* ---------- header ---------- */
.brandline{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.35rem 0 .9rem}
.brandmark{display:flex;align-items:center;gap:.75rem;font-size:1.15rem;font-weight:700;letter-spacing:-.045em;color:var(--ink)}
.brandseal{width:38px;height:38px;display:grid;place-items:center;border-radius:50%;background:radial-gradient(circle at 30% 25%,#d2382d,#7a1710);color:#ffe7a8;font-family:'Noto Serif Kannada',serif;font-size:1.15rem;font-weight:700;box-shadow:0 0 0 2px var(--card),0 0 0 3.5px var(--gold),0 8px 16px -6px rgba(120,20,12,.6)}
.brandmeta{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--bronze)}
.flagbar{display:flex;flex-direction:column;height:5px;margin:0 0 1.7rem;border-radius:3px;overflow:hidden;transform-origin:left;animation:barIn 1.2s var(--ease) .2s both}
.flagbar i{display:block;flex:1}.flagbar i:first-child{background:#FFC20E}.flagbar i:last-child{background:#C8102E}
.eyebrow{font-size:.72rem;letter-spacing:.19em;text-transform:uppercase;font-weight:700;color:var(--bronze)}
.zari{height:14px;background:linear-gradient(135deg,#e8a317 25%,transparent 25%) -7px 0/14px 14px,linear-gradient(225deg,#e8a317 25%,transparent 25%) -7px 0/14px 14px,linear-gradient(315deg,#e8a317 25%,transparent 25%) 0 0/14px 14px,linear-gradient(45deg,#e8a317 25%,#8c1c13 25%) 0 0/14px 14px}

/* ---------- landing hero ---------- */
.hero-shell{position:relative;isolation:isolate;overflow:hidden;min-height:580px;border:1px solid rgba(201,160,90,.6);border-radius:20px;background:linear-gradient(105deg,rgba(255,253,246,.97) 0%,rgba(255,249,232,.92) 42%,rgba(255,224,165,.6) 100%);box-shadow:0 40px 90px -40px rgba(80,40,10,.5),0 2px 0 rgba(255,255,255,.9) inset;padding:clamp(28px,5vw,68px);padding-bottom:clamp(44px,6vw,80px);display:flex;align-items:center;animation:riseIn 1s var(--ease) .1s both;margin-bottom:1.4rem}
.hero-shell:before{content:"";position:absolute;inset:0;z-index:-2;background:radial-gradient(ellipse at 78% 35%,rgba(217,154,30,.2),transparent 40%),linear-gradient(135deg,transparent 48%,rgba(148,101,54,.05) 48.2%,transparent 48.6%)}
.hero-copy{position:relative;z-index:4;max-width:600px}
.hello{display:inline-flex;align-items:center;gap:.7rem;font-family:'Noto Serif Kannada',serif;font-weight:700;font-size:1.1rem;color:var(--kum);margin-bottom:.9rem}
.hello:after{content:"";width:54px;height:2px;background:linear-gradient(90deg,var(--gold),transparent)}
.hero-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(3rem,6.2vw,5.9rem);font-weight:600;line-height:.98;letter-spacing:-.065em;color:var(--ink);margin:1rem 0 .9rem}
.hero-title em{font-weight:500;background:linear-gradient(120deg,var(--kum),var(--gold));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero-kn{font-family:'Noto Serif Kannada','Noto Sans Kannada',serif;font-size:clamp(1.05rem,1.7vw,1.4rem);font-weight:600;color:var(--maroon);margin-bottom:1.1rem}
.hero-description{font-size:1.04rem;line-height:1.85;color:#5d5144;max-width:510px}
.hero-foot,.heritage{margin-top:1.4rem;display:flex;gap:8px;flex-wrap:wrap}
.chip{padding:.32rem .85rem;border:1px solid rgba(148,101,54,.35);border-radius:999px;background:rgba(255,254,250,.65);font-size:.78rem;color:#6a5b48;transition:transform .3s var(--ease),background .3s}
.chip:hover{transform:translateY(-2px);background:#fff}
.heritage .chip{font-family:'Noto Serif Kannada',serif;border-color:rgba(164,35,27,.3);color:var(--maroon)}
.hero-zari{position:absolute;left:0;right:0;bottom:0;z-index:6}
.hero-progress{position:absolute;left:0;bottom:14px;height:3px;z-index:6;background:linear-gradient(90deg,var(--gold),var(--kum));box-shadow:0 0 12px rgba(217,154,30,.8);animation:fillBar 4.5s linear 1s both}
.culture-scene{position:absolute;right:0;bottom:0;width:56%;height:100%;z-index:1;perspective:1300px;perspective-origin:50% 35%;pointer-events:none;animation:sceneIn 1.5s var(--ease) .3s both}
.sun{position:absolute;right:16%;top:6%;width:48%;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle,#fff6d6 0 20%,#ffd37a 38%,rgba(255,190,90,.38) 60%,transparent 72%);animation:breath 7s ease-in-out infinite}
.sun .rays{position:absolute;inset:-38%;border-radius:50%;background:repeating-conic-gradient(from 0deg,rgba(255,196,96,.26) 0 4deg,transparent 4deg 14deg);-webkit-mask-image:radial-gradient(circle,#000 18%,transparent 62%);mask-image:radial-gradient(circle,#000 18%,transparent 62%);animation:spinZ 100s linear infinite}
.hill,.ground{-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 38%);mask-image:linear-gradient(90deg,transparent 0,#000 38%)}.hill{position:absolute;left:-6%;right:-6%;bottom:0}
.hill.h1{height:54%;background:linear-gradient(180deg,#d4bd8f,#ecdfbd);clip-path:polygon(0 72%,10% 54%,22% 63%,36% 38%,52% 58%,66% 34%,80% 55%,100% 40%,100% 100%,0 100%);opacity:.9;animation:drift 18s ease-in-out infinite}
