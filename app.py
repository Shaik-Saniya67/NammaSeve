import os
import time
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
.hill.h2{height:38%;background:linear-gradient(180deg,#b79864,#d6bf88);clip-path:polygon(0 50%,14% 30%,30% 52%,48% 26%,64% 50%,82% 28%,100% 46%,100% 100%,0 100%);opacity:.85;animation:drift 24s ease-in-out infinite reverse}
.ground{position:absolute;left:0;right:0;bottom:0;height:13%;background:linear-gradient(180deg,#d9bd88,#b99259)}
.g-shadow{position:absolute;right:4%;bottom:8.5%;width:50%;height:6%;background:radial-gradient(ellipse,rgba(60,30,10,.5),transparent 70%);filter:blur(7px)}
.gopuram{position:absolute;right:17%;bottom:12%;width:30em;height:40em;font-size:clamp(7px,.85vw,11px);transform-style:preserve-3d;transform:rotateY(-26deg) rotateX(4deg);animation:sway 10s ease-in-out infinite}
.gopuram.mini{right:50%;bottom:13.5%;font-size:clamp(4px,.5vw,6.4px);animation-delay:-4s;opacity:.92}
.bx{position:absolute;left:50%;bottom:calc(var(--y)*1em);width:calc(var(--w)*1em);height:calc(var(--h)*1em);margin-left:calc(var(--w)*-.5em);transform-style:preserve-3d}
.bx i{position:absolute;display:block}
.bx .f{inset:0;transform:translateZ(calc(var(--d)*.5em))}
.bx .s{left:100%;top:0;height:100%;width:calc(var(--d)*1em);transform-origin:left center;transform:translateZ(calc(var(--d)*.5em)) rotateY(90deg)}
.base .f{background:linear-gradient(180deg,#e2bd84,#a97a45)}.base .s{background:linear-gradient(180deg,#a97a45,#7e5630)}
.tier .f{background:radial-gradient(ellipse .7em 1.1em at 50% 100%,#2c150b 60%,transparent 64%) 0 62%/2.6em 2.2em repeat-x,linear-gradient(180deg,rgba(255,255,255,.22),transparent 25%,rgba(60,28,8,.22)),repeating-linear-gradient(90deg,transparent 0 2.45em,rgba(80,40,14,.32) 2.45em 2.6em),linear-gradient(90deg,#c99a5e,#ecd0a0 50%,#c3945a);box-shadow:inset 0 -.45em 0 var(--kum),inset 0 .25em 0 var(--gold)}
.tier .s{background:repeating-linear-gradient(90deg,transparent 0 1.9em,rgba(50,25,8,.4) 1.9em 2.05em),linear-gradient(180deg,rgba(0,0,0,.05),rgba(40,18,5,.35)),linear-gradient(90deg,#a97a45,#8b6234);box-shadow:inset 0 -.45em 0 #7c1a14,inset 0 .25em 0 #b07d14}
.cor .f{background:linear-gradient(180deg,#f6cf6a,#b9780f)}.cor .s{background:linear-gradient(180deg,#b9780f,#7d4f08)}
.crown .f{background:linear-gradient(90deg,#d9a032,#fbdc82 50%,#c58a1a);border-radius:50% 50% 0 0/90% 90% 0 0}
.crown .s{background:linear-gradient(180deg,#b9780f,#7d4f08);border-radius:0 40% 0 0/0 90% 0 0}
.door{position:absolute;left:50%;bottom:0;width:5em;height:4.2em;margin-left:-2.5em;border-radius:2.5em 2.5em 0 0;background:radial-gradient(ellipse at 50% 100%,#ffcf70 0,#c9741a 38%,#3a1a0d 75%);box-shadow:0 0 0 .3em rgba(224,165,35,.7),0 0 2em .6em rgba(255,170,50,.55)}
.kalasha{position:absolute;left:50%;bottom:calc(var(--y)*1em);width:0;height:0}
.kalasha b{position:absolute;bottom:0;left:-.45em;width:.9em;height:2.8em;background:linear-gradient(90deg,#b9780f,#ffe08a,#b9780f);border-radius:.45em .45em 0 0;box-shadow:0 0 1.2em rgba(255,200,80,.8)}
.kalasha b:nth-child(2){left:-2.2em;height:1.9em}.kalasha b:nth-child(3){left:1.3em;height:1.9em}
.diya{position:absolute;width:.6rem;height:.6rem;border-radius:50%;background:#ffe19a;box-shadow:0 0 14px 6px rgba(255,170,40,.65);animation:flicker 2.6s ease-in-out infinite}
.diya.d1{right:6%;bottom:9%}.diya.d2{right:36%;bottom:7%;animation-delay:-.8s}.diya.d3{right:2%;bottom:20%;animation-delay:-1.6s}.diya.d4{right:44%;bottom:10%;animation-delay:-2s}

/* ---------- cards & content ---------- */
.feature-number{font-family:'Playfair Display',serif;font-size:1.7rem;background:linear-gradient(120deg,var(--kum),var(--gold));-webkit-background-clip:text;background-clip:text;color:transparent}
.feature-title{font-weight:700;margin:.3rem 0}.feature-desc{font-size:.88rem;line-height:1.6;color:var(--muted)}
.paper-card{position:relative;overflow:hidden;background:linear-gradient(145deg,rgba(255,254,250,.94),rgba(255,249,234,.8));-webkit-backdrop-filter:blur(14px) saturate(1.2);backdrop-filter:blur(14px) saturate(1.2);border:1px solid rgba(201,160,90,.45);border-radius:16px;padding:clamp(18px,3vw,30px);box-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 26px 50px -26px rgba(70,40,15,.38),0 2px 6px rgba(70,40,15,.05);transition:transform .6s var(--ease),box-shadow .6s var(--ease);animation:riseIn .8s var(--ease) both}
.paper-card:before{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:linear-gradient(90deg,var(--kum),var(--gold),var(--kum));opacity:.85}
.paper-card:hover{transform:perspective(900px) rotateX(2.5deg) translateY(-6px);box-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 38px 60px -28px rgba(70,40,15,.45)}
.paper-card:not(.whole):has(.card-kicker){background:rgba(255,252,243,.93);border-bottom:0;border-bottom-left-radius:0;border-bottom-right-radius:0;box-shadow:0 1px 0 rgba(255,255,255,.9) inset}
.paper-card:not(.whole):has(.card-kicker):hover{transform:none}
.element-container:has(.paper-card:not(.whole) .card-kicker){margin-bottom:-1rem}
.element-container:has(.paper-card:not(.whole) .card-kicker)+*{position:relative;width:100%!important;background:rgba(255,252,243,.93);border:1px solid rgba(201,160,90,.45);border-top:0;border-radius:0 0 16px 16px;padding:.2rem clamp(18px,3vw,30px) 1.5rem;box-shadow:0 26px 50px -26px rgba(70,40,15,.38);animation:riseIn .8s var(--ease) .1s both}
[data-testid="stAudio"]{background:rgba(255,254,250,.8);border:1px solid rgba(201,160,90,.4);border-radius:14px;padding:.6rem}
[data-testid="stColumn"]:nth-child(2) .paper-card{animation-delay:.12s}[data-testid="stColumn"]:nth-child(3) .paper-card{animation-delay:.24s}
.card-kicker{font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:var(--kum);font-weight:700}
.subtle{color:var(--muted);font-size:.9rem;line-height:1.7}
.section-rule{height:1px;background:linear-gradient(90deg,var(--gold),var(--line) 40%,transparent);margin:1.1rem 0}
.source-box{background:linear-gradient(90deg,#fbf2da,#fffaf0);border-left:3px solid var(--kum);padding:15px 17px;color:#3e3023;line-height:1.85;border-radius:0 12px 12px 0;font-family:'Noto Serif Kannada','Noto Sans Kannada',serif}
.footer-note{text-align:center;color:#887a66;font-size:.78rem;line-height:1.7;padding-top:2.4rem}

/* ---------- Streamlit widgets ---------- */
div.stButton>button,div.stFormSubmitButton>button{position:relative;overflow:hidden;border-radius:12px;min-height:3rem;padding:.65rem 1.4rem;font-weight:700;border:1px solid rgba(201,160,90,.75);background:linear-gradient(180deg,#fffefa,#f6ecd4);color:var(--ink);box-shadow:0 1px 0 #fff inset,0 8px 18px -10px rgba(70,40,15,.45);transition:transform .4s var(--ease),box-shadow .4s var(--ease),background .4s,border-color .4s}
div.stButton>button:after,div.stFormSubmitButton>button:after{content:"";position:absolute;top:0;left:-70%;width:40%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.4),transparent);transform:skewX(-20deg);transition:left .8s var(--ease)}
div.stButton>button:hover,div.stFormSubmitButton>button:hover{transform:translateY(-3px);border-color:var(--gold);box-shadow:0 16px 28px -12px rgba(70,40,15,.45);color:var(--ink)}
div.stButton>button:hover:after,div.stFormSubmitButton>button:hover:after{left:140%}
div.stButton>button:active,div.stFormSubmitButton>button:active{transform:translateY(0) scale(.985)}
div.stButton>button p,div.stFormSubmitButton>button p{color:inherit!important}
div.stButton>button[kind="primary"],div.stFormSubmitButton>button[kind="primaryFormSubmit"],[data-testid="stBaseButton-primary"],[data-testid="stBaseButton-primaryFormSubmit"]{background:linear-gradient(135deg,#b3261e,#6a150e 75%);border-color:#5B140F;color:#fff6e3;box-shadow:0 14px 28px -12px rgba(120,20,12,.75),inset 0 1px 0 rgba(255,255,255,.25)}
div.stButton>button[kind="primary"]:hover,div.stFormSubmitButton>button[kind="primaryFormSubmit"]:hover,[data-testid="stBaseButton-primary"]:hover,[data-testid="stBaseButton-primaryFormSubmit"]:hover{background:linear-gradient(135deg,#c82f26,#7c1b13 75%);border-color:var(--gold);color:#fff}
[data-testid="stFileUploaderDropzone"]{background:linear-gradient(145deg,rgba(255,253,245,.95),rgba(251,240,212,.7));border:1.5px dashed #c9a25f;border-radius:16px;padding:1.2rem;transition:transform .45s var(--ease),box-shadow .45s var(--ease),border-color .3s}
[data-testid="stFileUploaderDropzone"]:hover{transform:translateY(-3px);border-color:var(--kum);box-shadow:0 22px 40px -24px rgba(120,60,20,.55)}
[data-testid="stSelectbox"] [role="group"],[data-testid="stTextInput"] [role="group"],[data-testid="stTextInputRootElement"],[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stTextInput"] [data-baseweb="input"],[data-testid="stTextInput"] [data-baseweb="base-input"]{background:rgba(255,254,250,.94)!important;border:1px solid #d8c29a!important;border-radius:12px!important;transition:border-color .3s,box-shadow .3s}
[data-baseweb="popover"] ul,[data-baseweb="menu"]{background:#FFFEFA!important;border-radius:12px}
[data-testid="stSelectbox"] [role="group"]:hover,[data-testid="stSelectbox"] [data-baseweb="select"]>div:hover{border-color:var(--gold)!important}
[data-testid="stTextInputRootElement"]:focus-within,[data-testid="stTextInput"] [role="group"]:focus-within{border-color:var(--gold)!important;box-shadow:0 0 0 4px rgba(217,154,30,.22)}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"] input{background:transparent!important}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within{border-color:var(--gold);box-shadow:0 0 0 4px rgba(217,154,30,.22)}
[data-testid="stTextInput"] input{padding:.8rem 1rem}
[data-testid="stExpander"]{background:rgba(255,254,250,.82);border:1px solid rgba(201,160,90,.45);border-radius:14px;overflow:hidden;transition:box-shadow .4s var(--ease)}
[data-testid="stExpander"]:hover{box-shadow:0 18px 34px -24px rgba(70,40,15,.5)}
[data-testid="stForm"]{border:0;padding:0}
.stAlert{border-radius:12px}
[data-testid="stSpinner"]{color:var(--bronze)}
audio{width:100%;border-radius:14px}

/* ---------- motion ---------- */
@keyframes riseIn{from{opacity:0;transform:translateY(26px) scale(.985)}to{opacity:1;transform:none}}
@keyframes sceneIn{from{opacity:0;transform:translateX(40px) scale(.95)}to{opacity:1;transform:none}}
@keyframes sway{0%,100%{transform:rotateY(-26deg) rotateX(4deg) translateY(0)}50%{transform:rotateY(-19deg) rotateX(4deg) translateY(-7px)}}
@keyframes breath{0%,100%{opacity:.8;transform:scale(.97)}50%{opacity:1;transform:scale(1.04)}}
@keyframes spinZ{to{transform:rotate(360deg)}}
@keyframes spinF{from{transform:rotateX(72deg) rotate(0)}to{transform:rotateX(72deg) rotate(360deg)}}
@keyframes spinM{from{transform:perspective(1100px) rotateX(16deg) rotateY(-26deg) rotate(0)}to{transform:perspective(1100px) rotateX(16deg) rotateY(-26deg) rotate(360deg)}}
@keyframes floaty{0%,100%{transform:translate3d(0,0,0)}50%{transform:translate3d(14px,-26px,0)}}
@keyframes rise{to{transform:translateY(-840px)}}
@keyframes drift{0%,100%{transform:translateX(-8px)}50%{transform:translateX(12px)}}
@keyframes flicker{0%,100%{opacity:.75;transform:scale(.9)}40%{opacity:1;transform:scale(1.15)}70%{opacity:.85;transform:scale(1)}}
@keyframes curOpen{to{transform:translateX(var(--x))}}
@keyframes emblem{0%{opacity:0;transform:translate(-50%,-50%) scale(.85)}35%{opacity:1;transform:translate(-50%,-50%) scale(1)}75%{opacity:1}100%{opacity:0;transform:translate(-50%,-50%) scale(1.12)}}
@keyframes veilOut{0%{opacity:1}100%{opacity:0;visibility:hidden}}
@keyframes barIn{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes fillBar{from{width:0}to{width:100%}}
@media(max-width:800px){.hero-shell{min-height:840px;align-items:flex-start;padding-bottom:330px}.hero-copy{max-width:100%}.culture-scene{width:100%;height:42%;opacity:.92}.hero-title{font-size:3.2rem}.brandmeta{display:none}.gopuram.mini{display:none}.gopuram{right:22%;font-size:6.8px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important;scroll-behavior:auto!important}.veil{display:none}}
</style>
""", unsafe_allow_html=True)

LANGUAGES = {
    "ಕನ್ನಡ · Kannada": "Kannada",
    "తెలుగు · Telugu": "Telugu",
    "हिन्दी · Hindi": "Hindi",
    "English": "English",
}
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def get_client():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        try:
            key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        except Exception:
            key = ""
    return Groq(api_key=key) if key else None


def groq_text(client, system, user, temperature=0.1):
    result = client.chat.completions.create(
        model=MODEL,
        temperature=temperature,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return (result.choices[0].message.content or "").strip()


def _gopuram_html():
    """Pure markup: a 3D Dravidian temple tower built from CSS boxes."""
    tiers = [(24, 7, 11), (20, 6, 9), (16, 5.2, 7.5), (12.5, 4.4, 6), (9, 3.8, 4.5)]
    y = 2.2
    parts = ['<div class="bx base" style="--w:30;--h:2.2;--d:14;--y:0"><i class="f"></i><i class="s"></i></div>']
    for n, (w, h, d) in enumerate(tiers):
        door = '<b class="door"></b>' if n == 0 else ''
        parts.append(f'<div class="bx tier" style="--w:{w};--h:{h};--d:{d};--y:{round(y, 2)}"><i class="f">{door}</i><i class="s"></i></div>')
        y += h
        parts.append(f'<div class="bx cor" style="--w:{w + 1.6};--h:.7;--d:{d + 1.2};--y:{round(y, 2)}"><i class="f"></i><i class="s"></i></div>')
        y += .7
    parts.append(f'<div class="bx crown" style="--w:6.5;--h:3;--d:3.5;--y:{round(y, 2)}"><i class="f"></i><i class="s"></i></div>')
    parts.append(f'<div class="kalasha" style="--y:{round(y + 3, 2)}"><b></b><b></b><b></b></div>')
    return "".join(parts)


WORLD_HTML = ('<div class="world" aria-hidden="true"><div class="mandala"></div><div class="orb o1"></div><div class="orb o2"></div>'
              '<div class="orb o3"></div><div class="floor"><div class="plane"></div><div class="plane p2"></div></div>'
              '<div class="petals"></div><div class="grain"></div></div>')


def brand_header(app_mode=False):
    veil = '<div class="veil soft"></div>' if app_mode else '<div class="veil curtain"><i></i><i></i><b>ನ</b></div>'
    st.markdown(f"""
    {veil}{WORLD_HTML}
    <div class="brandline">
      <div class="brandmark"><span class="brandseal">ನ</span><span>NammaSeve</span></div>
      <div class="brandmeta">{ 'PUBLIC NOTICE COMPANION' if app_mode else 'KARNATAKA · PUBLIC INFORMATION' }</div>
    </div>
    <div class="flagbar"><i></i><i></i></div>
    """, unsafe_allow_html=True)


def render_landing():
    brand_header(False)
    gopuram = _gopuram_html()
    st.markdown(f"""
    <section class="hero-shell">
      <div class="hero-copy">
        <div class="hello">ನಮಸ್ಕಾರ</div>
        <div class="eyebrow">A clearer way to access public information</div>
        <div class="hero-title">Understand<br>what <em>matters.</em></div>
        <div class="hero-kn">ಪ್ರತಿ ಕನ್ನಡ ಸೂಚನೆಯನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ</div>
        <div class="hero-description">Public notices shouldn't feel difficult to understand. Bring a Kannada notice to NammaSeve and discover its meaning in your language—with the original words always close at hand.</div>
        <div class="hero-foot"><span class="chip">ಕನ್ನಡ</span><span class="chip">తెలుగు</span><span class="chip">हिन्दी</span><span class="chip">English</span></div>
        <div class="heritage"><span class="chip">ಹಂಪಿ</span><span class="chip">ಮೈಸೂರು</span><span class="chip">ಬೇಲೂರು</span><span class="chip">ಹಳೇಬೀಡು</span><span class="chip">ಬಾದಾಮಿ</span></div>
      </div>
      <div class="culture-scene" aria-hidden="true">
        <div class="sun"><i class="rays"></i></div>
        <div class="hill h1"></div><div class="hill h2"></div><div class="ground"></div><div class="g-shadow"></div>
        <div class="gopuram mini">{gopuram}</div>
        <div class="gopuram">{gopuram}</div>
        <i class="diya d1"></i><i class="diya d2"></i><i class="diya d3"></i><i class="diya d4"></i>
      </div>
      <div class="hero-progress"></div><div class="zari hero-zari"></div>
    </section>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1], gap="small")
    with c1:
        st.markdown('<div class="paper-card"><div class="feature-number">01</div><div class="feature-title">Bring your notice</div><div class="feature-desc">Upload a PDF, scan, or photo of a Kannada public notice.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="paper-card"><div class="feature-number">02</div><div class="feature-title">Understand the essentials</div><div class="feature-desc">Get a plain-language explanation in the language you choose.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="paper-card"><div class="feature-number">03</div><div class="feature-title">Ask with confidence</div><div class="feature-desc">Ask questions and see the original notice sentence behind the answer.</div></div>', unsafe_allow_html=True)
    st.write("")
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        if st.button("Enter NammaSeve  ↗", type="primary", use_container_width=True, key="start_landing"):
            st.session_state.page = "app"
            st.session_state.landing_started = time.time()
            st.rerun()
    st.markdown('<div class="footer-note">Rooted in Karnataka. Designed for understanding.<br>Answers are grounded in the notice—not assumptions.</div>', unsafe_allow_html=True)


def render_app():
    brand_header(True)
    top_left, top_right = st.columns([1.7, 1], vertical_alignment="center")
    with top_left:
        st.markdown('<div class="eyebrow">YOUR NOTICE, MADE CLEAR</div>', unsafe_allow_html=True)
        st.markdown("# Understand what matters.")
        st.markdown('<p class="subtle">A thoughtful reading companion for Kannada public notices. Upload a document to begin.</p>', unsafe_allow_html=True)
    with top_right:
        lang_label = st.selectbox("Explanation language", list(LANGUAGES.keys()), index=3, key="main_lang")
        if st.button("← Home", key="back_home"):
            st.session_state.page = "landing"
            st.session_state.landing_started = time.time()
            st.rerun()
    target_language = LANGUAGES[lang_label]

    st.markdown('<div class="paper-card"><div class="card-kicker">STEP 01 · ADD A DOCUMENT</div><h3 style="margin:.55rem 0 .3rem">Bring your Kannada notice</h3><p class="subtle">Text PDFs are read directly. Scanned PDFs and photos use OCR, when available.</p>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a notice", type=["pdf", "png", "jpg", "jpeg", "webp"], help="PDF, PNG, JPG, JPEG and WEBP are supported.")
    st.markdown('</div>', unsafe_allow_html=True)

    if not uploaded:
        st.write("")
        st.markdown('<div class="paper-card whole"><div class="card-kicker">DESIGNED AROUND TRUST</div><h3 style="margin:.55rem 0">The source stays in view.</h3><p class="subtle">NammaSeve is designed to explain, not replace, the notice. You can inspect the extracted original text and check supporting Kannada sentences for answers.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="footer-note">NammaSeve · Understand every Kannada notice, clearly.</div>', unsafe_allow_html=True)
        return

    current_file_id = f"{uploaded.name}:{uploaded.size}"
    if st.session_state.get("file_id") != current_file_id:
        st.session_state.file_id = current_file_id
        st.session_state.notice_text = ""
        st.session_state.summary = ""
        st.session_state.chat_history = []
        st.session_state.audio_bytes = None

    st.write("")
    if st.button("Read and explain notice  →", type="primary", use_container_width=True, key="process"):
        with st.spinner("Reading the notice carefully…"):
            try:
                extracted = extract_text(uploaded.name, uploaded.getvalue())
                if len(extracted.strip()) < 20:
                    st.error("We couldn't extract enough text. Try a clearer photo or a text-based PDF.")
                else:
                    client = get_client()
                    if not client:
                        st.error("Add your Groq API key to the .env file beside app.py, then restart NammaSeve.")
                    else:
                        system = f"""You are NammaSeve, a careful public-notice explainer. Explain only what is supported by the notice. Do not invent dates, fees, eligibility, documents, locations, or actions. If a detail is absent or unclear, say 'Not clearly stated in the notice.' Answer in {target_language}, using simple accessible language. Organize the response under: What this notice is about; Important dates; What the reader needs to do; Fees and documents. Include a detail only if supported by the notice. If something is not mentioned, say so. Keep it concise."""
                        summary = groq_text(client, system, f"Explain this Kannada public notice in {target_language}. Preserve exact factual meaning. Do not add assumptions.\n\nNOTICE TEXT:\n{extracted[:24000]}")
                        st.session_state.notice_text = extracted
                        st.session_state.summary = summary
                        st.session_state.chat_history = []
                        st.session_state.audio_bytes = None
            except Exception as exc:
                st.error(f"Could not process the notice: {exc}")

    notice_text = st.session_state.get("notice_text", "")
    summary = st.session_state.get("summary", "")
    if not summary:
        return

    st.write("")
    st.markdown('<div class="paper-card"><div class="card-kicker">STEP 02 · THE ESSENTIALS</div><h3 style="margin:.55rem 0 1rem">Your notice, explained</h3>', unsafe_allow_html=True)
    st.markdown(summary)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown('<div class="paper-card"><div class="card-kicker">LISTEN</div><h3 style="margin:.55rem 0 .5rem">Hear the explanation</h3><p class="subtle">Listen in your selected language.</p>', unsafe_allow_html=True)
        if st.button("Prepare audio", key="audio"):
            with st.spinner("Preparing audio…"):
                try:
                    st.session_state.audio_bytes = make_audio(summary, target_language)
                except Exception as exc:
                    st.warning(f"Audio generation failed: {exc}")
        if st.session_state.get("audio_bytes"):
            st.audio(st.session_state.audio_bytes, format="audio/mp3")
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="paper-card"><div class="card-kicker">VERIFY</div><h3 style="margin:.55rem 0 .5rem">Original notice text</h3><p class="subtle">Check the extracted text against the document you uploaded.</p>', unsafe_allow_html=True)
        with st.expander("View extracted text"):
            st.text(notice_text)
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="paper-card"><div class="card-kicker">STEP 03 · ASK THE NOTICE</div><h3 style="margin:.55rem 0 .35rem">A question on your mind?</h3><p class="subtle">Ask in Kannada, Telugu, Hindi, or English. Answers should rely only on this notice and include the original supporting sentence.</p>', unsafe_allow_html=True)
    with st.form("ask_form", clear_on_submit=True):
        question = st.text_input("Your question", placeholder="For example: What documents do I need?")
        ask = st.form_submit_button("Find answer  →", type="primary")
    if ask and question.strip():
        client = get_client()
        if not client:
            st.error("Groq API key is missing. Add it to .env and restart the app.")
        else:
            with st.spinner("Looking for evidence in your notice…"):
                try:
                    system = f"""You are NammaSeve's grounded document question-answering assistant. Answer the user's question in {target_language}. Understand questions written in Kannada, Telugu, Hindi, or English. Use ONLY the supplied notice text. Never use outside knowledge or guess. Return exactly these sections: ANSWER: a concise answer in {target_language}, or 'This information is not mentioned in the notice.' SUPPORTING KANNADA SENTENCE: copy the exact supporting sentence(s) from the original notice text without translating or paraphrasing. If no sentence supports the answer, write 'No supporting sentence found in the notice.' If evidence is ambiguous or conflicting, say so. Never fabricate a quote."""
                    prompt = f"NOTICE TEXT:\n{notice_text[:24000]}\n\nUSER QUESTION:\n{question}\n\nAnswer in {target_language} and cite the exact supporting original sentence."
                    answer = groq_text(client, system, prompt)
                    st.session_state.chat_history.append({"q": question, "a": answer})
                except Exception as exc:
                    st.error(f"Couldn't answer this question: {exc}")
    for item in st.session_state.get("chat_history", []):
        st.markdown("**Your question**")
        st.write(item["q"])
        answer = item["a"]
        if "SUPPORTING KANNADA SENTENCE:" in answer:
            answer_part, source_part = answer.split("SUPPORTING KANNADA SENTENCE:", 1)
            st.markdown("**Answer**")
            st.write(answer_part.replace("ANSWER:", "").strip())
            st.markdown("**Original sentence cited**")
            st.markdown(f'<div class="source-box">{source_part.strip()}</div>', unsafe_allow_html=True)
        else:
            st.write(answer)
        st.markdown('<div class="section-rule"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="footer-note">NammaSeve supports understanding; it does not replace official clarification from the issuing authority.</div>', unsafe_allow_html=True)


if "page" not in st.session_state:
    st.session_state.page = "landing"
if "landing_started" not in st.session_state:
    st.session_state.landing_started = time.time()

if st.session_state.page == "landing":
    render_landing()
    # Auto-enter after a short pause; the CTA always allows immediate entry.
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=250, limit=20, key="nammaseve_landing_transition")
        if time.time() - st.session_state.landing_started >= 4.5:
            st.session_state.page = "app"
            st.rerun()
    except ImportError:
        pass
else:
    render_app()
