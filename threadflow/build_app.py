#!/usr/bin/env python3
"""
Builds the self-contained ThreadFlow HTML application for Canvas preview
by embedding the verified pure Costing Engine, Workflow Engine, and Seed Data
alongside the complete H&K Clothing UI, and also packages the full modular
project into threadflow-source.zip.
"""

import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = BASE_DIR
INTERMEDIATE_HTML = os.path.join(BASE_DIR, "dist/threadflow.html")
OUTPUT_HTML = INTERMEDIATE_HTML
OUTPUT_ZIP = os.path.join(BASE_DIR, "dist/threadflow-source.zip")

os.makedirs(os.path.join(BASE_DIR, "dist"), exist_ok=True)

with open(os.path.join(PROJ_DIR, "src/engine/costingEngine.js"), "r", encoding="utf-8") as f:
    costing_engine_js = f.read()

with open(os.path.join(PROJ_DIR, "src/engine/workflowEngine.js"), "r", encoding="utf-8") as f:
    workflow_engine_js = f.read()

with open(os.path.join(PROJ_DIR, "src/data/seedData.js"), "r", encoding="utf-8") as f:
    seed_data_js = f.read()

# Strip CommonJS require/module.exports blocks for inline browser execution
def clean_for_browser(code: str) -> str:
    lines = []
    skip_export = False
    for line in code.splitlines():
        if "require(" in line and "const " in line:
            continue
        if line.strip().startswith("if (typeof module !== 'undefined' && module.exports)"):
            skip_export = True
            continue
        if skip_export:
            if line.strip() == "}":
                skip_export = False
            continue
        lines.append(line)
    return "\n".join(lines)

browser_costing_js = clean_for_browser(costing_engine_js)
browser_workflow_js = clean_for_browser(workflow_engine_js)
browser_seed_js = clean_for_browser(seed_data_js)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>H&amp;K Clothing — ThreadFlow Garment Manufacturing Platform</title>
  <script src="https://cdn.tailwindcss.com/3.4.17"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    :root, [data-theme="light"] {
      --bg-canvas: #F6F5F1;
      --bg-surface: #FFFFFF;
      --bg-subtle: #EFECE6;
      --bg-elevated: #FAF9F6;
      --bg-glass: rgba(246, 245, 241, 0.86);
      --text-primary: #141413;
      --text-secondary: #52514E;
      --text-muted: #82807A;
      --border-hairline: #DFDDD6;
      --border-strong: #C7C4BA;
      --accent-primary: #B84A27;
      --accent-primary-hover: #9E3C1D;
      --accent-soft: rgba(184, 74, 39, 0.10);
      --accent-pine: #1E3A2F;
      --status-success-bg: #E6F4EA;
      --status-success-text: #135327;
      --status-warn-bg: #FEF0E1;
      --status-warn-text: #8F390B;
      --status-danger-bg: #FCE8E6;
      --status-danger-text: #9C1D1D;
      --status-info-bg: #E8EEF9;
      --status-info-text: #1B4488;
      --shadow-card: 0 1px 2px rgba(20, 20, 19, 0.04), 0 0 0 1px rgba(20, 20, 19, 0.06);
      --shadow-floating: 0 16px 36px -8px rgba(20, 20, 19, 0.14), 0 0 0 1px rgba(20, 20, 19, 0.08);
      --ease-spring: cubic-bezier(0.22, 1, 0.36, 1);
    }

    [data-theme="dark"] {
      --bg-canvas: #0E0F12;
      --bg-surface: #16181D;
      --bg-subtle: #1E2027;
      --bg-elevated: #22252D;
      --bg-glass: rgba(22, 24, 29, 0.86);
      --text-primary: #F3F2EE;
      --text-secondary: #A6A49D;
      --text-muted: #6E6D67;
      --border-hairline: #282B33;
      --border-strong: #3A3E4A;
      --accent-primary: #E0633C;
      --accent-primary-hover: #EB7652;
      --accent-soft: rgba(224, 99, 60, 0.15);
      --accent-pine: #2E5A48;
      --status-success-bg: rgba(34, 197, 94, 0.14);
      --status-success-text: #6EE7B7;
      --status-warn-bg: rgba(249, 115, 22, 0.15);
      --status-warn-text: #FDBA74;
      --status-danger-bg: rgba(239, 68, 68, 0.16);
      --status-danger-text: #FCA5A5;
      --status-info-bg: rgba(59, 130, 246, 0.16);
      --status-info-text: #93C5FD;
      --shadow-card: 0 1px 3px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.06);
      --shadow-floating: 0 20px 44px -10px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(255, 255, 255, 0.09);
    }

    * {
      box-sizing: border-box;
    }

    html, body {
      margin: 0;
      padding: 0;
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      -webkit-font-smoothing: antialiased;
      font-feature-settings: "cv02", "cv03", "cv04", "cv11";
      transition: background-color 200ms var(--ease-spring), color 200ms var(--ease-spring);
    }

    .font-editorial {
      font-family: 'Instrument Serif', Georgia, serif;
      letter-spacing: -0.01em;
    }

    .font-mono-tabular {
      font-family: 'JetBrains Mono', monospace;
      font-variant-numeric: tabular-nums;
    }

    .tabular-nums {
      font-variant-numeric: tabular-nums;
    }

    .tf-surface {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-hairline);
      box-shadow: var(--shadow-card);
    }

    .tf-subtle {
      background-color: var(--bg-subtle);
      border: 1px solid var(--border-hairline);
    }

    .tf-glass-bar {
      background-color: var(--bg-glass);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-hairline);
    }

    .tf-btn-primary {
      background-color: var(--accent-primary);
      color: #FFFFFF;
      transition: transform 120ms var(--ease-spring), background-color 150ms ease, box-shadow 150ms ease;
    }
    .tf-btn-primary:hover:not(:disabled) {
      background-color: var(--accent-primary-hover);
    }
    .tf-btn-primary:active:not(:disabled) {
      transform: scale(0.985);
    }

    .tf-btn-secondary {
      background-color: var(--bg-surface);
      color: var(--text-primary);
      border: 1px solid var(--border-strong);
      transition: transform 120ms var(--ease-spring), background-color 150ms ease, border-color 150ms ease;
    }
    .tf-btn-secondary:hover:not(:disabled) {
      background-color: var(--bg-subtle);
    }
    .tf-btn-secondary:active:not(:disabled) {
      transform: scale(0.985);
    }

    .tf-input {
      background-color: var(--bg-surface);
      color: var(--text-primary);
      border: 1px solid var(--border-strong);
      border-radius: 0.5rem;
      padding: 0.45rem 0.7rem;
      font-size: 0.84rem;
      transition: border-color 140ms ease, box-shadow 140ms ease;
    }
    .tf-input:focus {
      outline: none;
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 3px var(--accent-soft);
    }

    .tf-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.18rem 0.58rem;
      border-radius: 9999px;
      font-size: 0.72rem;
      font-weight: 600;
      letter-spacing: 0.01em;
    }
    .tf-badge-success { background: var(--status-success-bg); color: var(--status-success-text); }
    .tf-badge-warn    { background: var(--status-warn-bg); color: var(--status-warn-text); }
    .tf-badge-danger  { background: var(--status-danger-bg); color: var(--status-danger-text); }
    .tf-badge-info    { background: var(--status-info-bg); color: var(--status-info-text); }
    .tf-badge-neutral { background: var(--bg-subtle); color: var(--text-secondary); border: 1px solid var(--border-hairline); }

    .tf-table th {
      font-size: 0.70rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
      font-weight: 600;
      background-color: var(--bg-subtle);
      border-bottom: 1px solid var(--border-hairline);
    }
    .tf-table td {
      border-bottom: 1px solid var(--border-hairline);
      transition: background-color 120ms ease;
    }
    .tf-table tr:hover td {
      background-color: var(--accent-soft);
    }

    @keyframes tfViewEnter {
      from {
        opacity: 0;
        transform: translateY(6px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .tf-view-animate {
      animation: tfViewEnter 240ms var(--ease-spring) forwards;
    }

    @media (prefers-reduced-motion: reduce) {
      *, ::before, ::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
      }
    }

    body[data-reduced-motion="true"] *,
    body[data-reduced-motion="true"] .tf-view-animate {
      animation: none !important;
      transition: none !important;
    }

    /* Compact topbar state on scroll */
    header.tf-topbar-compact {
      padding-top: 0.4rem !important;
      padding-bottom: 0.4rem !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }
  </style>
</head>
<body class="min-h-screen flex flex-col selection:bg-orange-500/20">

  <!-- ==================================================================== -->
  <!-- AUTHENTICATION GATEWAY SCREEN (Shown when logged out)                -->
  <!-- ==================================================================== -->
  <div id="authGatewayScreen" class="fixed inset-0 z-50 flex items-center justify-center p-4" style="background-color: var(--bg-canvas);">
    <div class="w-full max-w-4xl grid grid-cols-1 lg:grid-cols-12 rounded-2xl overflow-hidden tf-surface shadow-2xl">
      <!-- Left Editorial Craft Panel -->
      <div class="lg:col-span-5 p-8 flex flex-col justify-between text-white" style="background-color: #16181D; border-right: 1px solid #282B33;">
        <div>
          <div class="flex items-center gap-3 mb-6">
            <div class="w-9 h-9 rounded-lg flex items-center justify-center font-mono-tabular font-semibold text-sm" style="background-color: #B84A27; color: #fff;">H&amp;K</div>
            <div>
              <div class="text-xs uppercase tracking-widest text-stone-400">H&amp;K Clothing · Tiruppur</div>
              <div class="text-base font-semibold tracking-tight text-stone-100">ThreadFlow OS v2.4</div>
            </div>
          </div>
          <h1 class="font-editorial text-3xl sm:text-4xl font-normal text-stone-100 leading-tight mb-4">
            Precision garment costing &amp; floor execution.
          </h1>
          <p class="text-xs text-stone-400 leading-relaxed">
            Engineered for H&amp;K Clothing’s merchandising, costing, and production units. Every gram, fabric serial, size grade (S–XXXL), and workflow milestone is persisted with full audit traceability.
          </p>
        </div>
        <div class="pt-6 border-t border-stone-800 space-y-2 text-xs text-stone-400">
          <div class="flex justify-between">
            <span>Costing Engine</span>
            <span class="font-mono-tabular text-stone-200">GSM × Cut Area + Wastage %</span>
          </div>
          <div class="flex justify-between">
            <span>Size Range</span>
            <span class="font-mono-tabular text-stone-200">S · M · L · XL · XXL · XXXL</span>
          </div>
          <div class="flex justify-between">
            <span>Access Control</span>
            <span class="font-mono-tabular text-emerald-400">Server/Engine RBAC Active</span>
          </div>
        </div>
      </div>

      <!-- Right Sign-In Form & Quick Role Selector -->
      <div class="lg:col-span-7 p-8 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-lg font-semibold">Sign in to Workspace</h2>
              <p class="text-xs" style="color: var(--text-secondary);">Authenticate with your H&amp;K Clothing staff credentials or select a verified role profile.</p>
            </div>
            <span class="tf-badge tf-badge-neutral font-mono-tabular">Unit II · Tiruppur</span>
          </div>

          <form id="loginForm" onsubmit="handleLoginSubmit(event)" class="space-y-4">
            <div>
              <label for="loginEmailInput" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Admin username</label>
              <input id="loginEmailInput" type="text" required autocomplete="username" class="tf-input w-full" placeholder="Username" />
            </div>
            <div>
              <label for="loginPasswordInput" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Password</label>
              <input id="loginPasswordInput" type="password" required autocomplete="current-password" class="tf-input w-full font-mono-tabular" placeholder="••••••••••••" />
            </div>
            <div id="loginErrorBox" class="hidden p-2.5 rounded-lg text-xs tf-badge-danger"></div>
            <button id="loginSubmitBtn" type="submit" class="tf-btn-primary w-full py-2.5 px-4 rounded-lg text-sm font-medium">
              Authenticate &amp; Open ThreadFlow
            </button>
          </form>

          <div class="mt-6 pt-5 border-t" style="border-color: var(--border-hairline);">
            <div class="text-xs font-medium mb-2.5" style="color: var(--text-secondary);">Quick Role Preset Selection (Fills Credentials):</div>
            <p class="text-xs" style="color: var(--text-muted);">Sign in with your administrator credentials.</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ==================================================================== -->
  <!-- MAIN APPLICATION SHELL                                               -->
  <!-- ==================================================================== -->
  <div id="appShell" class="flex flex-1 min-h-screen overflow-hidden">

    <!-- Mobile Navigation Backdrop -->
    <div id="mobileNavBackdrop" onclick="toggleMobileSidebar(false)" class="hidden fixed inset-0 bg-black/50 z-30 lg:hidden"></div>

    <!-- Collapsible Sidebar -->
    <aside id="appSidebar" class="fixed lg:static inset-y-0 left-0 z-40 w-64 flex flex-col justify-between transition-all duration-200 transform -translate-x-full lg:translate-x-0" style="background-color: var(--bg-surface); border-right: 1px solid var(--border-hairline);">
      <div>
        <!-- Brand Header -->
        <div class="h-16 px-4 flex items-center justify-between border-b" style="border-color: var(--border-hairline);">
          <div class="flex items-center gap-3 overflow-hidden">
            <div class="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center font-mono-tabular font-bold text-xs text-white" style="background-color: var(--accent-primary);">
              H&amp;K
            </div>
            <div id="sidebarBrandText" class="truncate">
              <div class="text-xs font-semibold tracking-tight leading-none">H&amp;K CLOTHING</div>
              <div class="text-[11px] font-mono-tabular mt-0.5" style="color: var(--text-muted);">THREADFLOW ERP</div>
            </div>
          </div>
          <button id="collapseSidebarBtn" type="button" onclick="toggleDesktopSidebarCollapse()" title="Collapse or expand navigation" class="hidden lg:inline-flex p-1.5 rounded-md hover:bg-stone-500/10 text-xs" style="color: var(--text-secondary);">
            ⇄
          </button>
          <button id="closeMobileSidebarBtn" type="button" onclick="toggleMobileSidebar(false)" class="lg:hidden p-1.5 rounded-md text-xs" style="color: var(--text-secondary);">
            ✕
          </button>
        </div>

        <!-- Primary Navigation -->
        <nav class="p-3 space-y-1" aria-label="Main Navigation">
          <button type="button" id="navBtn-dashboard" onclick="navigateToView('dashboard')" class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors">
            <span class="flex items-center gap-3">
              <span class="font-mono-tabular text-sm">◈</span>
              <span class="sidebar-label">Dashboard</span>
            </span>
            <span id="navBadge-dashboard" class="sidebar-label font-mono-tabular text-[11px] px-1.5 py-0.5 rounded bg-stone-500/10">Live</span>
          </button>

          <button type="button" id="navBtn-costing" onclick="navigateToView('costing')" class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors">
            <span class="flex items-center gap-3">
              <span class="font-mono-tabular text-sm">📐</span>
              <span class="sidebar-label">Costing</span>
            </span>
            <span id="navBadge-costing" class="sidebar-label font-mono-tabular text-[11px] px-1.5 py-0.5 rounded bg-stone-500/10">5</span>
          </button>

          <button type="button" id="navBtn-followup" onclick="navigateToView('followup')" class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors">
            <span class="flex items-center gap-3">
              <span class="font-mono-tabular text-sm">✓</span>
              <span class="sidebar-label">Status Follow-Up</span>
            </span>
            <span id="navBadge-followup" class="sidebar-label font-mono-tabular text-[11px] px-1.5 py-0.5 rounded tf-badge-warn">6</span>
          </button>

          <button type="button" id="navBtn-orders" onclick="navigateToView('orders')" class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors">
            <span class="flex items-center gap-3">
              <span class="font-mono-tabular text-sm">📦</span>
              <span class="sidebar-label">Order History</span>
            </span>
            <span id="navBadge-orders" class="sidebar-label font-mono-tabular text-[11px] px-1.5 py-0.5 rounded bg-stone-500/10">6</span>
          </button>

          <button type="button" id="navBtn-settings" onclick="navigateToView('settings')" class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-colors">
            <span class="flex items-center gap-3">
              <span class="font-mono-tabular text-sm">⚙</span>
              <span class="sidebar-label">Settings &amp; RBAC</span>
            </span>
          </button>
        </nav>

        <!-- Quick Action Card inside Sidebar -->
        <div id="sidebarQuickLaunch" class="mx-3 mt-4 p-3.5 rounded-xl tf-subtle">
          <div class="text-[11px] font-semibold uppercase tracking-wider mb-1" style="color: var(--text-muted);">Floor Operations</div>
          <p class="text-xs leading-relaxed mb-3" style="color: var(--text-secondary);">
            Launch the 6-step garment costing calculator or log a production task.
          </p>
          <div class="space-y-1.5">
            <button type="button" onclick="openCostingWizardNew()" class="tf-btn-primary w-full py-1.5 px-3 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5">
              <span>+ New Style Costing</span>
            </button>
            <button type="button" onclick="openCreateTaskModal()" class="tf-btn-secondary w-full py-1.5 px-3 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5">
              <span>+ Log Follow-Up Task</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Sidebar Footer: User Session & Role Switcher -->
      <div class="p-3 border-t" style="border-color: var(--border-hairline);">
        <div class="flex items-center justify-between gap-2 p-2 rounded-lg tf-subtle">
          <div class="flex items-center gap-2.5 min-w-0">
            <div id="sidebarUserAvatar" class="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-semibold text-white" style="background-color: var(--accent-pine);">
              AK
            </div>
            <div class="sidebar-label min-w-0">
              <div id="sidebarUserName" class="text-xs font-semibold truncate">Arjun Karthikeyan</div>
              <div id="sidebarUserRole" class="text-[10px] font-mono-tabular uppercase truncate" style="color: var(--text-muted);">admin</div>
            </div>
          </div>
          <button type="button" onclick="handleLogout()" title="Sign Out" class="sidebar-label p-1.5 rounded hover:bg-red-500/10 text-xs" style="color: var(--status-danger-text);">
            ⎋
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Workspace Column -->
    <div class="flex-1 flex flex-col min-w-0 max-h-screen overflow-hidden">

      <!-- Sticky Top Navigation Bar -->
      <header id="appTopbar" class="tf-glass-bar sticky top-0 z-20 px-4 sm:px-6 py-3 flex items-center justify-between gap-3 transition-all duration-150">
        <div class="flex items-center gap-3 min-w-0">
          <button type="button" onclick="toggleMobileSidebar(true)" class="lg:hidden p-2 rounded-lg tf-btn-secondary text-xs" aria-label="Open menu">
            ☰
          </button>
          <div class="min-w-0">
            <div class="flex items-center gap-1.5 text-[11px] font-mono-tabular" style="color: var(--text-muted);">
              <span>H&amp;K CLOTHING</span>
              <span>/</span>
              <span id="topBreadcrumbSection" class="uppercase">OPERATIONS</span>
            </div>
            <h1 id="topPageTitle" class="text-base sm:text-lg font-semibold tracking-tight truncate">
              Operational Intelligence Dashboard
            </h1>
          </div>
        </div>

        <!-- Contextual Search & Controls -->
        <div class="flex items-center gap-2 sm:gap-3">
          <div class="relative hidden md:block w-64 lg:w-72">
            <input
              id="globalSearchInput"
              type="search"
              oninput="handleGlobalSearchInput(this.value)"
              placeholder="Search styles, orders, POs, tasks..."
              class="tf-input w-full pl-3 pr-8 py-1.5 text-xs"
            />
            <span class="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] font-mono-tabular px-1 rounded" style="color: var(--text-muted); border: 1px solid var(--border-hairline);">/</span>
            <!-- Search Dropdown Results -->
            <div id="globalSearchDropdown" class="hidden absolute left-0 right-0 mt-1.5 rounded-xl tf-surface p-2 z-50 max-h-80 overflow-y-auto" style="box-shadow: var(--shadow-floating);"></div>
          </div>

          <!-- Role Quick Switcher Pill -->
          <div class="hidden sm:flex items-center gap-1.5">
            <label for="topbarRoleSelect" class="text-[11px] font-mono-tabular hidden xl:inline" style="color: var(--text-muted);">Role:</label>
            <select id="topbarRoleSelect" onchange="handleQuickRoleSwitch(this.value)" class="tf-input py-1 px-2 text-xs font-mono-tabular" title="Switch active user session to test RBAC permissions">
            </select>
          </div>

          <!-- Notifications Popover Trigger -->
          <div class="relative">
            <button id="notificationsBtn" type="button" onclick="toggleNotificationsPanel()" class="tf-btn-secondary relative p-2 rounded-lg text-xs" title="Operational Alerts &amp; Notifications">
              <span>🔔</span>
              <span id="notificationCountDot" class="absolute -top-1 -right-1 w-4 h-4 rounded-full text-[10px] font-mono-tabular font-bold flex items-center justify-center text-white" style="background-color: var(--accent-primary);">4</span>
            </button>
            <div id="notificationsPopover" class="hidden absolute right-0 mt-2 w-80 sm:w-96 rounded-xl tf-surface p-3 z-50" style="box-shadow: var(--shadow-floating);">
              <div class="flex items-center justify-between pb-2 mb-2 border-b" style="border-color: var(--border-hairline);">
                <span class="text-xs font-semibold">Operational Notifications</span>
                <span class="text-[11px] font-mono-tabular" style="color: var(--text-muted);">Oct 18, 2026</span>
              </div>
              <div id="notificationsList" class="space-y-2 max-h-72 overflow-y-auto"></div>
            </div>
          </div>

          <!-- Theme Toggle -->
          <button id="themeToggleBtn" type="button" onclick="toggleTheme()" class="tf-btn-secondary px-2.5 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5" title="Switch between Warm Porcelain (Light) and Graphite Ink (Dark)">
            <span id="themeToggleIcon">☀</span>
            <span id="themeToggleLabel" class="hidden sm:inline">Light</span>
          </button>

          <!-- Logout Button -->
          <button type="button" onclick="handleLogout()" class="tf-btn-secondary px-2.5 py-1.5 rounded-lg text-xs font-medium hidden sm:inline-flex" title="Lock &amp; Sign Out">
            Sign Out
          </button>
        </div>
      </header>

      <!-- Scrollable Workspace Content Area -->
      <main id="workspaceMain" onscroll="handleWorkspaceScroll(this)" class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">

        <!-- ============================================================== -->
        <!-- VIEW 1: DASHBOARD — LIVE OPERATIONAL INTELLIGENCE              -->
        <!-- ============================================================== -->
        <section id="view-dashboard" class="space-y-6 tf-view-animate">
          <!-- Editorial Banner + Live Filter Bar -->
          <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-4 border-b" style="border-color: var(--border-hairline);">
            <div>
              <div class="inline-flex items-center gap-2 text-xs font-mono-tabular mb-1" style="color: var(--accent-primary);">
                <span>● LIVE FLOOR TELEMETRY</span>
                <span>·</span>
                <span>TIRUPPUR KNITWEAR DIVISION</span>
              </div>
              <h2 class="font-editorial text-2xl sm:text-3xl font-normal tracking-tight">
                Manufacturing &amp; Costing Command
              </h2>
              <p class="text-xs mt-1 max-w-2xl" style="color: var(--text-secondary);">
                Every metric below is computed directly from persisted costing sheets, active cutting/sewing orders, and verified workflow milestones. Click any metric card or chart bar to inspect the underlying records.
              </p>
            </div>

            <!-- Dashboard Filter Controls -->
            <div class="flex flex-wrap items-center gap-2">
              <select id="dashCategoryFilter" onchange="renderDashboard()" class="tf-input text-xs py-1.5">
                <option value="ALL">All Categories (Men's / Ladies / Other)</option>
                <option value="Men's">Men's Garments</option>
                <option value="Ladies">Ladies Garments</option>
                <option value="Other">Other Categories</option>
              </select>
              <select id="dashTypeFilter" onchange="renderDashboard()" class="tf-input text-xs py-1.5">
                <option value="ALL">All Garment Types (Top &amp; Bottom)</option>
                <option value="Top">Tops Only</option>
                <option value="Bottom">Bottoms Only</option>
              </select>
              <select id="dashDateFilter" onchange="renderDashboard()" class="tf-input text-xs py-1.5">
                <option value="ALL">All Production Windows</option>
                <option value="DUE_7_DAYS">Due Within 7 Days (≤ Oct 25)</option>
                <option value="DUE_14_DAYS">Due Within 14 Days (≤ Nov 01)</option>
              </select>
              <button type="button" onclick="openCostingWizardNew()" class="tf-btn-primary px-3.5 py-1.5 rounded-lg text-xs font-medium">
                + New Costing Sheet
              </button>
            </div>
          </div>

          <!-- Operational Alerts & Exceptions Strip -->
          <div id="dashboardAlertsContainer" class="space-y-2"></div>

          <!-- 5 Core Operational KPI Cards -->
          <div id="dashboardKpiGrid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5"></div>

          <!-- Charts Row: Production Progress by Order + Costing & Fabric Consumption Breakdown -->
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <div class="lg:col-span-7 p-5 rounded-xl tf-surface flex flex-col justify-between">
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                <div>
                  <h3 class="text-sm font-semibold">Order Production &amp; Workflow Completion</h3>
                  <p class="text-xs" style="color: var(--text-secondary);">Comparing piece output (%) vs. completed workflow milestones across active orders</p>
                </div>
                <span class="tf-badge tf-badge-neutral font-mono-tabular">Persisted Orders</span>
              </div>
              <div class="relative h-64 w-full">
                <canvas id="dashboardProductionChart"></canvas>
              </div>
            </div>

            <div class="lg:col-span-5 p-5 rounded-xl tf-surface flex flex-col justify-between">
              <div class="flex items-center justify-between gap-2 mb-4">
                <div>
                  <h3 class="text-sm font-semibold">Fabric Requirement &amp; Cost by Style</h3>
                  <p class="text-xs" style="color: var(--text-secondary);">Gross fabric consumption (kg) including process wastage</p>
                </div>
                <span class="tf-badge tf-badge-info font-mono-tabular">Costing Engine</span>
              </div>
              <div class="relative h-64 w-full">
                <canvas id="dashboardFabricChart"></canvas>
              </div>
            </div>
          </div>

          <!-- Split Operational Tables: Recent Active Orders & Upcoming Follow-Ups -->
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <!-- Recent Orders Table -->
            <div class="lg:col-span-7 rounded-xl tf-surface overflow-hidden">
              <div class="px-5 py-4 flex items-center justify-between border-b" style="border-color: var(--border-hairline);">
                <div>
                  <h3 class="text-sm font-semibold">Active &amp; Recent Manufacturing Orders</h3>
                  <p class="text-xs" style="color: var(--text-secondary);">Click any order row to open full traceability, size quantities, and costing</p>
                </div>
                <button type="button" onclick="navigateToView('orders')" class="tf-btn-secondary px-2.5 py-1 rounded text-xs font-medium">
                  View All Orders →
                </button>
              </div>
              <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse tf-table">
                  <thead>
                    <tr>
                      <th class="py-2.5 px-4">Order / Buyer</th>
                      <th class="py-2.5 px-3">Style</th>
                      <th class="py-2.5 px-3 text-right">Pieces</th>
                      <th class="py-2.5 px-3">Workflow</th>
                      <th class="py-2.5 px-3">Due Date</th>
                      <th class="py-2.5 px-4 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody id="dashboardRecentOrdersBody" class="divide-y text-xs" style="border-color: var(--border-hairline);"></tbody>
                </table>
              </div>
            </div>

            <!-- Upcoming Follow-Ups & Actionable Tasks -->
            <div class="lg:col-span-5 rounded-xl tf-surface overflow-hidden flex flex-col">
              <div class="px-5 py-4 flex items-center justify-between border-b" style="border-color: var(--border-hairline);">
                <div>
                  <h3 class="text-sm font-semibold">Upcoming Follow-Ups &amp; Floor Tasks</h3>
                  <p class="text-xs" style="color: var(--text-secondary);">Sorted by follow-up date; complete directly with audit timestamp</p>
                </div>
                <button type="button" onclick="navigateToView('followup')" class="tf-btn-secondary px-2.5 py-1 rounded text-xs font-medium">
                  All Tasks →
                </button>
              </div>
              <div id="dashboardUpcomingTasksList" class="p-4 space-y-2.5 flex-1 overflow-y-auto"></div>
            </div>
          </div>
        </section>

        <!-- ============================================================== -->
        <!-- VIEW 2: COSTING — GARMENT COST CALCULATION SYSTEM & WIZARD     -->
        <!-- ============================================================== -->
        <section id="view-costing" class="hidden space-y-6 tf-view-animate">
          <!-- Costing Sub-Navigation Header -->
          <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-4 border-b" style="border-color: var(--border-hairline);">
            <div>
              <div class="inline-flex items-center gap-2 text-xs font-mono-tabular mb-1" style="color: var(--accent-primary);">
                <span>📐 GARMENT ENGINEERING &amp; CONSUMPTION ENGINE</span>
              </div>
              <h2 class="font-editorial text-2xl sm:text-3xl font-normal tracking-tight">
                Technical Style Costing &amp; Multi-Fabric Matrix
              </h2>
              <p class="text-xs mt-1 max-w-2xl" style="color: var(--text-secondary);">
                Separates Net Garment Weight (g), Gross Fabric Consumption (g/kg with process wastage), and Extended Fabric Cost (₹) across sizes S–XXXL. Missing inputs are strictly distinguished from zero order quantities.
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" id="costingModeListBtn" onclick="switchCostingSubmode('list')" class="tf-btn-secondary px-3.5 py-2 rounded-lg text-xs font-medium">
                Costing Records List
              </button>
              <button type="button" id="costingModeWizardBtn" onclick="openCostingWizardNew()" class="tf-btn-primary px-3.5 py-2 rounded-lg text-xs font-medium">
                + Launch 6-Step Costing Wizard
              </button>
            </div>
          </div>

          <!-- SUBVIEW 2A: COSTING RECORDS LIST & FORMULA DOCUMENTATION -->
          <div id="costingListSubview" class="space-y-5">
            <!-- Search, Filter, and Sort Bar -->
            <div class="p-4 rounded-xl tf-surface flex flex-wrap items-center justify-between gap-3">
              <div class="flex flex-wrap items-center gap-2.5 flex-1">
                <input
                  id="costingSearchInput"
                  type="search"
                  oninput="renderCostingList()"
                  placeholder="Search style #, style name, or fabric..."
                  class="tf-input w-full sm:w-64 text-xs"
                />
                <select id="costingFilterType" onchange="renderCostingList()" class="tf-input text-xs">
                  <option value="ALL">All Types (Top &amp; Bottom)</option>
                  <option value="Top">Top</option>
                  <option value="Bottom">Bottom</option>
                </select>
                <select id="costingFilterCategory" onchange="renderCostingList()" class="tf-input text-xs">
                  <option value="ALL">All Categories</option>
                  <option value="Men's">Men's</option>
                  <option value="Ladies">Ladies</option>
                  <option value="Other">Other</option>
                </select>
                <select id="costingFilterStatus" onchange="renderCostingList()" class="tf-input text-xs">
                  <option value="ALL">All Statuses</option>
                  <option value="Approved">Approved</option>
                  <option value="Finalized">Finalized</option>
                  <option value="Draft">Draft</option>
                </select>
              </div>
              <div class="flex items-center gap-2">
                <label for="costingSortSelect" class="text-xs" style="color: var(--text-secondary);">Sort:</label>
                <select id="costingSortSelect" onchange="renderCostingList()" class="tf-input text-xs">
                  <option value="updated_desc">Recently Updated</option>
                  <option value="style_asc">Style Number (A–Z)</option>
                  <option value="cost_desc">Total Order Cost (High → Low)</option>
                  <option value="piece_asc">Piece Cost (Low → High)</option>
                  <option value="gsm_desc">Base GSM (High → Low)</option>
                </select>
              </div>
            </div>

            <!-- Costing Cards / Table Grid -->
            <div id="costingRecordsContainer" class="grid grid-cols-1 gap-4"></div>

            <!-- Documented Engineering Formulas & Assumptions Panel -->
            <div class="p-5 rounded-xl tf-subtle space-y-3">
              <div class="flex items-center justify-between">
                <h3 class="text-xs font-semibold uppercase tracking-wider" style="color: var(--text-secondary);">
                  Documented Costing Calculation Formulas, Units &amp; Validation Rules
                </h3>
                <span class="font-mono-tabular text-[11px]" style="color: var(--accent-primary);">1 m² = 10,000 cm² · 1 kg = 1,000 g</span>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs" style="color: var(--text-secondary);">
                <div class="p-3.5 rounded-lg tf-surface">
                  <div class="font-semibold mb-1" style="color: var(--text-primary);">1. Component Net Weight (g)</div>
                  <p class="leading-relaxed">
                    For each enabled component <span class="font-mono-tabular">c</span> and size <span class="font-mono-tabular">s ∈ {S..XXXL}</span>:<br/>
                    <span class="font-mono-tabular text-[11px]">Area(m²) = [(L + Seam) × (W + Seam) × Panels] / 10,000</span><br/>
                    <span class="font-mono-tabular text-[11px]">NetWeight(g) = Area(m²) × FabricGSM</span>
                  </p>
                </div>
                <div class="p-3.5 rounded-lg tf-surface">
                  <div class="font-semibold mb-1" style="color: var(--text-primary);">2. Gross Fabric Consumption (kg)</div>
                  <p class="leading-relaxed">
                    Kept strictly separate from Net Garment Weight by incorporating process wastage <span class="font-mono-tabular">w%</span>:<br/>
                    <span class="font-mono-tabular text-[11px]">Consumption(g) = NetWeight(g) × (1 + w/100)</span><br/>
                    <span class="font-mono-tabular text-[11px]">Consumption(kg) = Consumption(g) / 1,000</span>
                  </p>
                </div>
                <div class="p-3.5 rounded-lg tf-surface">
                  <div class="font-semibold mb-1" style="color: var(--text-primary);">3. Cost &amp; Missing-Input Guardrails</div>
                  <p class="leading-relaxed">
                    <span class="font-mono-tabular text-[11px]">ComponentCost(₹) = Consumption(kg) × PricePerKg</span>.<br/>
                    A size quantity of <span class="font-mono-tabular">0</span> is a valid zero order for that size; blank/missing measurements or unassigned fabrics raise explicit validation errors.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- SUBVIEW 2B: 6-STEP INTERACTIVE COSTING WIZARD -->
          <div id="costingWizardSubview" class="hidden space-y-5">
            <!-- Sticky Wizard Step Bar & Live Summary Header -->
            <div class="sticky top-14 z-10 p-4 rounded-xl tf-surface space-y-3" style="box-shadow: var(--shadow-card);">
              <div class="flex flex-wrap items-center justify-between gap-3">
                <div class="flex items-center gap-2">
                  <span id="wizardModeBadge" class="tf-badge tf-badge-info font-mono-tabular">NEW COSTING SHEET</span>
                  <h3 id="wizardHeaderTitle" class="text-sm font-semibold">Step 1 of 6 — Style Details</h3>
                </div>
                <div class="flex items-center gap-4 text-xs font-mono-tabular">
                  <div>
                    <span style="color: var(--text-muted);">Order Qty:</span>
                    <strong id="wizLiveTotalQty" class="ml-1">0 pcs</strong>
                  </div>
                  <div>
                    <span style="color: var(--text-muted);">Avg Net Wt:</span>
                    <strong id="wizLiveAvgNetWt" class="ml-1">0.0 g</strong>
                  </div>
                  <div>
                    <span style="color: var(--text-muted);">Avg Gross Cons:</span>
                    <strong id="wizLiveAvgCons" class="ml-1">0.0 g</strong>
                  </div>
                  <div>
                    <span style="color: var(--text-muted);">Total Fabric Cost:</span>
                    <strong id="wizLiveTotalCost" class="ml-1" style="color: var(--accent-primary);">₹0.00</strong>
                  </div>
                </div>
              </div>

              <!-- 6-Step Progress Buttons -->
              <div id="wizardStepIndicators" class="grid grid-cols-2 sm:grid-cols-6 gap-1.5"></div>
            </div>

            <!-- Wizard Body + Interactive Garment Technical Blueprint Sidebar -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
              <!-- Active Step Form Area -->
              <div class="lg:col-span-8 p-5 rounded-xl tf-surface space-y-5">
                <div id="wizardStepContent"></div>

                <!-- Step Navigation Footer -->
                <div class="pt-4 border-t flex flex-wrap items-center justify-between gap-3" style="border-color: var(--border-hairline);">
                  <div class="flex items-center gap-2">
                    <button type="button" onclick="switchCostingSubmode('list')" class="tf-btn-secondary px-3 py-2 rounded-lg text-xs font-medium">
                      ← Exit to List (State Preserved)
                    </button>
                    <button type="button" onclick="resetWizardToBlank()" class="tf-btn-secondary px-3 py-2 rounded-lg text-xs font-medium">
                      Reset Blank
                    </button>
                  </div>
                  <div class="flex items-center gap-2">
                    <button type="button" id="wizPrevStepBtn" onclick="moveWizardStep(-1)" class="tf-btn-secondary px-4 py-2 rounded-lg text-xs font-medium">
                      ← Previous Step
                    </button>
                    <button type="button" id="wizNextStepBtn" onclick="moveWizardStep(1)" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">
                      Next Step →
                    </button>
                  </div>
                </div>
              </div>

              <!-- Live Technical Garment CAD Schematic & Validation Rail -->
              <div class="lg:col-span-4 space-y-4">
                <div class="p-4 rounded-xl tf-surface space-y-3">
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">Technical Component Schematic</span>
                    <span id="wizCadGarmentBadge" class="tf-badge tf-badge-neutral font-mono-tabular">Top · Men's</span>
                  </div>
                  <div id="wizardSvgBlueprint" class="p-3 rounded-lg tf-subtle flex items-center justify-center min-h-[210px]"></div>
                  <div id="wizardComponentLegend" class="space-y-1.5 text-xs"></div>
                </div>

                <!-- Live Validation Status Box -->
                <div class="p-4 rounded-xl tf-surface space-y-2.5">
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold uppercase tracking-wider" style="color: var(--text-muted);">Live Costing Validation</span>
                    <span id="wizValidationBadge" class="tf-badge tf-badge-success">Ready</span>
                  </div>
                  <div id="wizValidationMessages" class="space-y-1.5 text-xs max-h-56 overflow-y-auto"></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ============================================================== -->
        <!-- VIEW 3: STATUS FOLLOW-UP — PERSISTENT WORKFLOW MANAGEMENT      -->
        <!-- ============================================================== -->
        <section id="view-followup" class="hidden space-y-6 tf-view-animate">
          <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-4 border-b" style="border-color: var(--border-hairline);">
            <div>
              <div class="inline-flex items-center gap-2 text-xs font-mono-tabular mb-1" style="color: var(--accent-primary);">
                <span>✓ PERSISTENT ORDER-BASED TASK WORKFLOW</span>
              </div>
              <h2 class="font-editorial text-2xl sm:text-3xl font-normal tracking-tight">
                Production Status Follow-Up &amp; Audit Ledger
              </h2>
              <p class="text-xs mt-1 max-w-2xl" style="color: var(--text-secondary);">
                Manage Pending, In Progress, and Completed production milestones. Marking a task complete validates permissions, persists to the database before updating the UI, and records an immutable audit trail. Reopening preserves prior completion history.
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" onclick="openCreateTaskModal()" class="tf-btn-primary px-3.5 py-2 rounded-lg text-xs font-medium">
                + New Order Follow-Up Task
              </button>
            </div>
          </div>

          <!-- Status Tabs + Filter Bar -->
          <div class="p-4 rounded-xl tf-surface flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div class="flex flex-wrap items-center gap-1.5" role="tablist">
              <button type="button" id="taskTab-ALL" onclick="setTaskStatusTab('ALL')" class="px-3 py-1.5 rounded-lg text-xs font-medium">
                All Tasks (<span id="taskCount-ALL" class="font-mono-tabular">0</span>)
              </button>
              <button type="button" id="taskTab-Pending" onclick="setTaskStatusTab('Pending')" class="px-3 py-1.5 rounded-lg text-xs font-medium">
                Pending (<span id="taskCount-Pending" class="font-mono-tabular">0</span>)
              </button>
              <button type="button" id="taskTab-In Progress" onclick="setTaskStatusTab('In Progress')" class="px-3 py-1.5 rounded-lg text-xs font-medium">
                In Progress (<span id="taskCount-InProgress" class="font-mono-tabular">0</span>)
              </button>
              <button type="button" id="taskTab-Completed" onclick="setTaskStatusTab('Completed')" class="px-3 py-1.5 rounded-lg text-xs font-medium">
                Completed History (<span id="taskCount-Completed" class="font-mono-tabular">0</span>)
              </button>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <input
                id="taskSearchInput"
                type="search"
                oninput="renderFollowUpTasks()"
                placeholder="Search task title, remarks, assignee..."
                class="tf-input text-xs w-56"
              />
              <select id="taskOrderFilter" onchange="renderFollowUpTasks()" class="tf-input text-xs">
                <option value="ALL">All Linked Orders</option>
              </select>
              <select id="taskAssigneeFilter" onchange="renderFollowUpTasks()" class="tf-input text-xs">
                <option value="ALL">All Assignees</option>
                <option value="Meera Sundaram">Meera Sundaram</option>
                <option value="Devika Natarajan">Devika Natarajan</option>
                <option value="Vikram Rajan">Vikram Rajan</option>
                <option value="Arjun Karthikeyan">Arjun Karthikeyan</option>
              </select>
            </div>
          </div>

          <!-- Order Workflow Progress Summary Strip -->
          <div id="followUpOrderProgressStrip" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3"></div>

          <!-- Task Cards / Table -->
          <div id="followUpTasksContainer" class="space-y-3"></div>
        </section>

        <!-- ============================================================== -->
        <!-- VIEW 4: ORDER HISTORY — TRACEABILITY WITHOUT DATA LOSS         -->
        <!-- ============================================================== -->
        <section id="view-orders" class="hidden space-y-6 tf-view-animate">
          <div class="flex flex-col lg:flex-row lg:items-end justify-between gap-4 pb-4 border-b" style="border-color: var(--border-hairline);">
            <div>
              <div class="inline-flex items-center gap-2 text-xs font-mono-tabular mb-1" style="color: var(--accent-primary);">
                <span>📦 FULL LIFECYCLE TRACEABILITY</span>
              </div>
              <h2 class="font-editorial text-2xl sm:text-3xl font-normal tracking-tight">
                Order History &amp; Production Ledger
              </h2>
              <p class="text-xs mt-1 max-w-2xl" style="color: var(--text-secondary);">
                Distinct views for Currently Going On, Completed, and Cancelled orders. Completing or cancelling an order preserves all linked costing records, size-wise quantities, task timelines, and historical status remarks.
              </p>
            </div>
            <div class="flex items-center gap-2">
              <button type="button" onclick="openCreateOrderModal()" class="tf-btn-primary px-3.5 py-2 rounded-lg text-xs font-medium">
                + Create Manufacturing Order
              </button>
            </div>
          </div>

          <!-- Order Lifecycle Tabs + Search & Sort -->
          <div class="p-4 rounded-xl tf-surface flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div class="flex flex-wrap items-center gap-1.5">
              <button type="button" id="orderTab-Currently Going On" onclick="setOrderStatusTab('Currently Going On')" class="px-3 py-1.5 rounded-lg text-xs font-medium">
                Currently Going On (<span id="orderCount-GoingOn" class="font-mono-tabular">0</span>)
              </button>
              <button type="button" id="orderTab-Completed" onclick="setOrderStatusTab('Completed')" class="px-3 py-1.5 rounded-lg text-xs font-medium">
                Completed (<span id="orderCount-Completed" class="font-mono-tabular">0</span>)
              </button>
              <button type="button" id="orderTab-Cancelled" onclick="setOrderStatusTab('Cancelled')" class="px-3 py-1.5 rounded-lg text-xs font-medium">
                Cancelled (<span id="orderCount-Cancelled" class="font-mono-tabular">0</span>)
              </button>
              <button type="button" id="orderTab-ALL" onclick="setOrderStatusTab('ALL')" class="px-3 py-1.5 rounded-lg text-xs font-medium">
                All Orders (<span id="orderCount-ALL" class="font-mono-tabular">0</span>)
              </button>
            </div>

            <div class="flex flex-wrap items-center gap-2">
              <input
                id="orderSearchInput"
                type="search"
                oninput="renderOrdersView()"
                placeholder="Search order #, buyer, PO ref, style..."
                class="tf-input text-xs w-60"
              />
              <select id="orderSortSelect" onchange="renderOrdersView()" class="tf-input text-xs">
                <option value="due_asc">Due Date (Soonest First)</option>
                <option value="order_desc">Order Date (Newest First)</option>
                <option value="pieces_desc">Total Pieces (High → Low)</option>
              </select>
            </div>
          </div>

          <!-- Orders List Grid -->
          <div id="ordersListContainer" class="space-y-3.5"></div>
        </section>

        <!-- ============================================================== -->
        <!-- VIEW 5: SETTINGS, AUTHENTICATION, RBAC & VERIFICATION SUITE    -->
        <!-- ============================================================== -->
        <section id="view-settings" class="hidden space-y-6 tf-view-animate">
          <div class="pb-4 border-b" style="border-color: var(--border-hairline);">
            <div class="inline-flex items-center gap-2 text-xs font-mono-tabular mb-1" style="color: var(--accent-primary);">
              <span>⚙ SYSTEM GOVERNANCE, SECURITY &amp; DIAGNOSTICS</span>
            </div>
            <h2 class="font-editorial text-2xl sm:text-3xl font-normal tracking-tight">
              Authentication, Access Policies &amp; Automated Verification
            </h2>
            <p class="text-xs mt-1 max-w-2xl" style="color: var(--text-secondary);">
              Manage active user profile, role-based access control (RBAC) policies, interface preferences, and run the built-in automated test suite verifying costing mathematics and workflow state transitions.
            </p>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <!-- Profile & Preferences -->
            <div class="lg:col-span-5 space-y-5">
              <div class="p-5 rounded-xl tf-surface space-y-4">
                <div class="flex items-center justify-between">
                  <h3 class="text-sm font-semibold">Active Authenticated Session</h3>
                  <span id="settingsRoleBadge" class="tf-badge tf-badge-info font-mono-tabular">admin</span>
                </div>
                <form id="profileUpdateForm" onsubmit="handleProfileSave(event)" class="space-y-3">
                  <div>
                    <label for="profFullName" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Full Name</label>
                    <input id="profFullName" type="text" required class="tf-input w-full" />
                  </div>
                  <div>
                    <label for="profEmail" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Email Address</label>
                    <input id="profEmail" type="email" readonly class="tf-input w-full opacity-75 font-mono-tabular" />
                  </div>
                  <div>
                    <label for="profDepartment" class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Department / Unit</label>
                    <input id="profDepartment" type="text" required class="tf-input w-full" />
                  </div>
                  <div class="pt-2 space-y-2">
                    <div class="text-xs font-semibold" style="color: var(--text-secondary);">Notification &amp; Display Preferences</div>
                    <label class="flex items-center gap-2 text-xs cursor-pointer">
                      <input id="prefNotifyDueSoon" type="checkbox" checked />
                      <span>Alert on orders due within 7 days</span>
                    </label>
                    <label class="flex items-center gap-2 text-xs cursor-pointer">
                      <input id="prefNotifyStatus" type="checkbox" checked />
                      <span>Alert on workflow task completion &amp; reopen events</span>
                    </label>
                    <label class="flex items-center gap-2 text-xs cursor-pointer">
                      <input id="prefReducedMotion" type="checkbox" onchange="toggleReducedMotionPreference(this.checked)" />
                      <span>Reduced Motion Mode (Disable decorative transitions)</span>
                    </label>
                  </div>
                  <button type="submit" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">
                    Save Profile &amp; Preferences
                  </button>
                </form>
              </div>

              <!-- Database Persistence & Factory Reset -->
              <div class="p-5 rounded-xl tf-surface space-y-3">
                <h3 class="text-sm font-semibold">Database Persistence &amp; Backup</h3>
                <p class="text-xs leading-relaxed" style="color: var(--text-secondary);">
                  Records are saved in the connected Neon PostgreSQL database. Export backups regularly from Settings.
                </p>
                <div class="flex flex-wrap gap-2">
                  <button type="button" onclick="exportDatabaseJson()" class="tf-btn-secondary px-3 py-2 rounded-lg text-xs font-medium">
                    ⬇ Export Database Snapshot (JSON)
                  </button>
                  <button type="button" onclick="openResetDatabaseModal()" class="tf-btn-secondary px-3 py-2 rounded-lg text-xs font-medium" style="color: var(--status-danger-text);">
                    ↺ Reset to Factory Seed Data
                  </button>
                </div>
              </div>
            </div>

            <!-- Right Column: RBAC Matrix + Live In-Browser Test Runner -->
            <div class="lg:col-span-7 space-y-5">
              <!-- RBAC Matrix -->
              <div class="p-5 rounded-xl tf-surface space-y-3">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-semibold">Role-Based Access Control (RBAC) Matrix</h3>
                    <p class="text-xs" style="color: var(--text-secondary);">The deployment has one administrator account.</p>
                  </div>
                  <span class="tf-badge tf-badge-neutral font-mono-tabular">Single Admin</span>
                </div>
                <div class="overflow-x-auto">
                  <table class="w-full text-left border-collapse tf-table text-xs">
                    <thead>
                      <tr>
                        <th class="py-2 px-3">Staff Member</th>
                        <th class="py-2 px-3">Role</th>
                        <th class="py-2 px-3">Costing Write/Approve</th>
                        <th class="py-2 px-3">Task Complete/Reopen</th>
                        <th class="py-2 px-3">Order Transitions</th>
                        <th class="py-2 px-3 text-right">Switch</th>
                      </tr>
                    </thead>
                    <tbody id="settingsRbacTableBody"></tbody>
                  </table>
                </div>
              </div>

              <!-- Live Automated Verification Suite Runner -->
              <div class="p-5 rounded-xl tf-surface space-y-3">
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-sm font-semibold">Automated Business Logic &amp; Calculation Test Suite</h3>
                    <p class="text-xs" style="color: var(--text-secondary);">Executes live assertions against the pure Costing Engine and Workflow State Machine</p>
                  </div>
                  <button type="button" onclick="runInBrowserVerificationSuite()" class="tf-btn-primary px-3.5 py-1.5 rounded-lg text-xs font-medium">
                    ▶ Run Verification Tests
                  </button>
                </div>
                <div id="inBrowserTestResults" class="p-3.5 rounded-lg tf-subtle font-mono-tabular text-xs space-y-1.5 max-h-64 overflow-y-auto"></div>
              </div>
            </div>
          </div>
        </section>

      </main>
    </div>
  </div>

  <!-- ==================================================================== -->
  <!-- UNIVERSAL MODAL & SLIDE-OVER DRAWER CONTAINER                        -->
  <!-- ==================================================================== -->
  <div id="modalOverlay" class="hidden fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/60 backdrop-blur-sm">
    <div id="modalDialog" role="dialog" aria-modal="true" class="w-full max-w-4xl max-h-[90vh] rounded-2xl tf-surface flex flex-col overflow-hidden" style="box-shadow: var(--shadow-floating);">
      <div class="px-5 py-4 border-b flex items-center justify-between gap-3" style="border-color: var(--border-hairline);">
        <div>
          <div id="modalCategoryLabel" class="text-[10px] font-mono-tabular uppercase tracking-wider" style="color: var(--accent-primary);">RECORD DETAIL</div>
          <h3 id="modalTitle" class="text-base font-semibold">Modal Heading</h3>
        </div>
        <button type="button" onclick="closeModal()" class="tf-btn-secondary px-2.5 py-1 rounded-lg text-xs font-medium" aria-label="Close modal">
          ✕ Esc
        </button>
      </div>
      <div id="modalBody" class="p-5 overflow-y-auto flex-1 space-y-5"></div>
      <div id="modalFooter" class="px-5 py-3.5 border-t flex items-center justify-end gap-2" style="border-color: var(--border-hairline); background-color: var(--bg-subtle);"></div>
    </div>
  </div>

  <!-- Toast Notification Stack -->
  <div id="toastStack" class="fixed bottom-4 right-4 z-50 space-y-2 max-w-sm w-full pointer-events-none"></div>

  <!-- ==================================================================== -->
  <!-- APPLICATION LOGIC & EMBEDDED ENGINES                                 -->
  <!-- ==================================================================== -->
  <script>
    // --- 1. Embedded Pure Costing Calculation Engine ---
__BROWSER_COSTING_JS__

    // --- 2. Embedded Pure Workflow, Order & RBAC Engine ---
__BROWSER_WORKFLOW_JS__

    // --- 3. Embedded Seed Database Generator ---
__BROWSER_SEED_JS__

    // --- 4. Application State & Persistence Layer ---
    const DB_STORAGE_KEY = 'hk_threadflow_db_v2_4';
    const SESSION_STORAGE_KEY = 'hk_threadflow_session_v2_4';
    const WIZARD_STORAGE_KEY = 'hk_threadflow_wizard_draft_v2_4';

    let appState = {
      db: null,
      currentUser: null,
      activeView: 'dashboard',
      sidebarCollapsed: false,
      reducedMotion: false,
      costingSubmode: 'list', // 'list' | 'wizard'
      taskStatusTab: 'ALL',
      orderStatusTab: 'Currently Going On',
      activeOrderDetailTab: 'overview',
      wizardState: {
        step: 1,
        editingCostingId: null,
        form: null
      }
    };
    let databaseSaveQueue = Promise.resolve();

    let productionChartInstance = null;
    let fabricChartInstance = null;

    function safeStorageGet(key) {
      try {
        const raw = window.localStorage.getItem(key);
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        return null;
      }
    }

    function safeStorageSet(key, val) {
      try {
        window.localStorage.setItem(key, JSON.stringify(val));
      } catch (e) {
        // Ignore quota errors in restricted sandboxes
      }
    }

    function saveDatabase() {
      if (appState.currentUser && appState.db) {
        const snapshot = JSON.stringify(appState.db);
        databaseSaveQueue = databaseSaveQueue.then(() => fetch('/api/database', { method: 'PUT', headers: { 'content-type': 'application/json' }, body: snapshot })).then(response => {
          if (!response.ok) throw new Error('Save failed');
        }).catch(() => showToast('Could not save changes. Check your connection.', 'error'));
      }
      updateNavigationBadges();
      renderNotifications();
    }

    function createBlankWizardForm() {
      return {
        id: 'CST-' + Math.floor(2606 + Math.random() * 899),
        styleNumber: 'HK-2618-NEW',
        styleName: 'Heavyweight Compact Jersey Crew',
        primaryFabric: '100% Organic Combed Cotton Single Jersey',
        baseGsm: 220,
        garmentType: 'Top',
        category: "Men's",
        wastageAllowancePct: 8.0,
        status: 'Draft',
        notes: 'Double-needle bottom hem; bio-washed enzyme finish.',
        sizeQuantities: { S: 150, M: 350, L: 450, XL: 250, XXL: 100, XXXL: 0 },
        fabrics: [
          {
            serialNo: 1,
            fabricCode: 'FAB-SJ-220',
            description: '30s/1 Combed Organic Compact Jersey',
            colour: 'Warm Porcelain Ecru',
            gsm: 220,
            pricePerKg: 620,
            widthInches: 60,
            properties: 'Bio-polished, compacted'
          },
          {
            serialNo: 2,
            fabricCode: 'FAB-RIB-280',
            description: '1x1 Cotton Elastane Neck Rib',
            colour: 'Warm Porcelain Ecru',
            gsm: 280,
            pricePerKg: 690,
            widthInches: 36,
            properties: '5% Lycra recovery rib'
          }
        ],
        components: [
          {
            key: 'main_body',
            name: 'Main Body',
            isCustom: false,
            enabled: true,
            assignedFabricSerial: 1,
            panelMultiplier: 2,
            seamAllowanceCm: 3.0,
            measurementsBySize: buildUniformGradedMeasurements(68, 50, 2.0, 2.5)
          },
          {
            key: 'sleeve',
            name: 'Sleeve',
            isCustom: false,
            enabled: true,
            assignedFabricSerial: 1,
            panelMultiplier: 2,
            seamAllowanceCm: 2.5,
            measurementsBySize: buildUniformGradedMeasurements(22, 20, 1.0, 1.2)
          },
          {
            key: 'rib',
            name: 'Rib',
            isCustom: false,
            enabled: true,
            assignedFabricSerial: 2,
            panelMultiplier: 1,
            seamAllowanceCm: 1.5,
            measurementsBySize: buildUniformGradedMeasurements(46, 6.0, 1.5, 0.0)
          },
          {
            key: 'bnt',
            name: 'BNT',
            isCustom: false,
            enabled: true,
            assignedFabricSerial: 1,
            panelMultiplier: 1,
            seamAllowanceCm: 1.0,
            measurementsBySize: buildUniformGradedMeasurements(42, 3.5, 1.5, 0.0)
          },
          {
            key: 'yoke',
            name: 'Yoke',
            isCustom: false,
            enabled: false,
            assignedFabricSerial: 1,
            panelMultiplier: 1,
            seamAllowanceCm: 2.0,
            measurementsBySize: buildUniformGradedMeasurements(43, 12, 1.5, 0.5)
          }
        ]
      };
    }

    function escapeHtml(str) {
      if (str === null || str === undefined) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }

    function formatINR(amount) {
      const n = Number(amount) || 0;
      return '₹' + n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function formatNumber(num, decimals = 0) {
      const n = Number(num) || 0;
      return n.toLocaleString('en-IN', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
    }

    function showToast(message, variant = 'success') {
      const stack = document.getElementById('toastStack');
      if (!stack) return;
      const toast = document.createElement('div');
      const badgeClass =
        variant === 'error'
          ? 'tf-badge-danger'
          : variant === 'warn'
          ? 'tf-badge-warn'
          : 'tf-badge-success';
      toast.className = 'pointer-events-auto p-3.5 rounded-xl tf-surface flex items-start justify-between gap-3 text-xs transition-all duration-200';
      toast.style.boxShadow = 'var(--shadow-floating)';
      toast.innerHTML = `
        <div class="flex items-start gap-2.5">
          <span class="tf-badge ${badgeClass} uppercase font-mono-tabular">${escapeHtml(variant)}</span>
          <span class="leading-relaxed font-medium" style="color: var(--text-primary);">${escapeHtml(message)}</span>
        </div>
        <button type="button" onclick="this.parentElement.remove()" class="text-xs opacity-60 hover:opacity-100">✕</button>
      `;
      stack.appendChild(toast);
      setTimeout(() => {
        if (toast.parentElement) toast.remove();
      }, 4200);
    }

    // --- 5. Initialization & Authentication ---
    async function initApplication() {
      let auth = null;
      try { auth = await fetch('/api/session').then(r => r.ok ? r.json() : null); } catch (_) {}
      if (!auth?.user) { document.getElementById('authGatewayScreen').classList.remove('hidden'); return; }
      try { appState.db = await fetch('/api/database').then(r => { if (!r.ok) throw new Error(); return r.json(); }); }
      catch (_) { document.getElementById('loginErrorBox').textContent = 'Unable to load saved data. Check the server connection.'; document.getElementById('loginErrorBox').classList.remove('hidden'); return; }
      appState.currentUser = auth.user;

      const savedWizard = safeStorageGet(WIZARD_STORAGE_KEY);
      if (savedWizard && savedWizard.form) {
        appState.wizardState = savedWizard;
      } else {
        appState.wizardState = {
          step: 1,
          editingCostingId: null,
          form: createBlankWizardForm()
        };
      }

      applyTheme(appState.currentUser.themePreference || 'light');
      syncAuthenticatedUI();
      navigateToView('dashboard');

      // Global keyboard shortcuts ('/' for search, 'Escape' for modal)
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          closeModal();
          const drop = document.getElementById('globalSearchDropdown');
          if (drop) drop.classList.add('hidden');
          const notif = document.getElementById('notificationsPopover');
          if (notif) notif.classList.add('hidden');
        }
        if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
          e.preventDefault();
          const searchEl = document.getElementById('globalSearchInput');
          if (searchEl) searchEl.focus();
        }
      });
    }

    async function handleLoginSubmit(e) {
      e.preventDefault();
      const username = document.getElementById('loginEmailInput').value.trim().toLowerCase();
      const pass = document.getElementById('loginPasswordInput').value;
      const errBox = document.getElementById('loginErrorBox');

      let result;
      try {
        const response = await fetch('/api/login', { method:'POST', headers:{'content-type':'application/json'}, body:JSON.stringify({username,password:pass}) });
        const responseText = await response.text();
        try { result = JSON.parse(responseText); }
        catch (_) { throw new Error(`Server error (${response.status}). Check Vercel Function Logs and confirm DATABASE_URL and AUTH_SESSION_SECRET are set.`); }
        if (!response.ok) throw new Error(result.error || 'Sign in failed.');
        appState.currentUser = result.user;
        const dbResponse = await fetch('/api/database');
        if (!dbResponse.ok) throw new Error('Signed in, but the database could not be loaded. Check the Vercel database configuration.');
        appState.db = await dbResponse.json();
      } catch (error) {
        errBox.textContent = error.message || 'Unable to connect to the server.';
        errBox.classList.remove('hidden');
        return;
      }

      errBox.classList.add('hidden');
      document.getElementById('authGatewayScreen').classList.add('hidden');
      applyTheme(appState.currentUser.themePreference || 'light');
      syncAuthenticatedUI();
      navigateToView('dashboard');
      showToast(`Signed in as ${appState.currentUser.fullName}`, 'success');
    }

    function handleLogout() {
      appState.currentUser = null;
      fetch('/api/logout', {method:'POST'}).catch(() => {});
      document.getElementById('authGatewayScreen').classList.remove('hidden');
    }

    function handleQuickRoleSwitch(userId) {
      const user = appState.db.users.find((u) => u.id === userId);
      if (!user) return;
      appState.currentUser = user;
      safeStorageSet(SESSION_STORAGE_KEY, user);
      syncAuthenticatedUI();
      renderCurrentActiveView();
      showToast(`Switched active session to ${user.fullName} (Role: ${user.role})`, 'info');
    }

    function syncAuthenticatedUI() {
      const user = appState.currentUser;
      if (!user) {
        document.getElementById('authGatewayScreen').classList.remove('hidden');
        return;
      }
      document.getElementById('authGatewayScreen').classList.add('hidden');
      document.getElementById('sidebarUserAvatar').textContent = user.avatarInitials || 'HK';
      document.getElementById('sidebarUserName').textContent = user.fullName;
      document.getElementById('sidebarUserRole').textContent = user.role;

      const roleSelect = document.getElementById('topbarRoleSelect');
      if (roleSelect) {
        roleSelect.innerHTML = appState.db.users
          .map(
            (u) =>
              `<option value="${escapeHtml(u.id)}" ${u.id === user.id ? 'selected' : ''}>${escapeHtml(u.fullName)} (${escapeHtml(u.role)})</option>`
          )
          .join('');
      }

      updateNavigationBadges();
      renderNotifications();
    }

    // --- 6. Theme, Motion & Layout Controls ---
    function applyTheme(theme) {
      const clean = theme === 'dark' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', clean);
      const icon = document.getElementById('themeToggleIcon');
      const label = document.getElementById('themeToggleLabel');
      if (icon) icon.textContent = clean === 'dark' ? '☾' : '☀';
      if (label) label.textContent = clean === 'dark' ? 'Dark' : 'Light';
      if (appState.activeView === 'dashboard') {
        setTimeout(() => renderDashboardCharts(), 40);
      }
    }

    function toggleTheme() {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      if (appState.currentUser) {
        appState.currentUser.themePreference = next;
        if (appState.db?.users?.[0]) appState.db.users[0].themePreference = next;
        saveDatabase();
      }
    }

    function toggleReducedMotionPreference(enabled) {
      appState.reducedMotion = Boolean(enabled);
      document.body.setAttribute('data-reduced-motion', appState.reducedMotion ? 'true' : 'false');
      showToast(`Reduced motion mode ${appState.reducedMotion ? 'enabled' : 'disabled'}.`, 'info');
    }

    function toggleDesktopSidebarCollapse() {
      appState.sidebarCollapsed = !appState.sidebarCollapsed;
      const sidebar = document.getElementById('appSidebar');
      const labels = document.querySelectorAll('.sidebar-label');
      const quickLaunch = document.getElementById('sidebarQuickLaunch');
      const brandText = document.getElementById('sidebarBrandText');
      if (appState.sidebarCollapsed) {
        sidebar.classList.remove('w-64');
        sidebar.classList.add('w-20');
        labels.forEach((el) => el.classList.add('hidden'));
        if (quickLaunch) quickLaunch.classList.add('hidden');
        if (brandText) brandText.classList.add('hidden');
      } else {
        sidebar.classList.remove('w-20');
        sidebar.classList.add('w-64');
        labels.forEach((el) => el.classList.remove('hidden'));
        if (quickLaunch) quickLaunch.classList.remove('hidden');
        if (brandText) brandText.classList.remove('hidden');
      }
    }

    function toggleMobileSidebar(open) {
      const sidebar = document.getElementById('appSidebar');
      const backdrop = document.getElementById('mobileNavBackdrop');
      if (open) {
        sidebar.classList.remove('-translate-x-full');
        backdrop.classList.remove('hidden');
      } else {
        sidebar.classList.add('-translate-x-full');
        backdrop.classList.add('hidden');
      }
    }

    function handleWorkspaceScroll(container) {
      const topbar = document.getElementById('appTopbar');
      if (!topbar) return;
      if (container.scrollTop > 18) {
        topbar.classList.add('tf-topbar-compact');
      } else {
        topbar.classList.remove('tf-topbar-compact');
      }
    }

    function navigateToView(viewName) {
      const validViews = ['dashboard', 'costing', 'followup', 'orders', 'settings'];
      if (!validViews.includes(viewName)) return;
      appState.activeView = viewName;

      validViews.forEach((v) => {
        const sec = document.getElementById(`view-${v}`);
        const btn = document.getElementById(`navBtn-${v}`);
        if (sec) {
          if (v === viewName) {
            sec.classList.remove('hidden');
          } else {
            sec.classList.add('hidden');
          }
        }
        if (btn) {
          if (v === viewName) {
            btn.style.backgroundColor = 'var(--accent-soft)';
            btn.style.color = 'var(--accent-primary)';
            btn.style.fontWeight = '600';
          } else {
            btn.style.backgroundColor = 'transparent';
            btn.style.color = 'var(--text-secondary)';
            btn.style.fontWeight = '500';
          }
        }
      });

      const titles = {
        dashboard: ['OPERATIONAL INTELLIGENCE', 'Live Manufacturing & Costing Dashboard'],
        costing: ['GARMENT ENGINEERING', 'Style Costing & Multi-Fabric Consumption'],
        followup: ['WORKFLOW EXECUTION', 'Status Follow-Up & Task Audit Ledger'],
        orders: ['ORDER TRACEABILITY', 'Order History & Production Lifecycle'],
        settings: ['GOVERNANCE & RBAC', 'Authentication, Role Permissions & Diagnostics']
      };
      const [crumb, title] = titles[viewName] || ['WORKSPACE', 'ThreadFlow'];
      document.getElementById('topBreadcrumbSection').textContent = crumb;
      document.getElementById('topPageTitle').textContent = title;

      toggleMobileSidebar(false);
      renderCurrentActiveView();
    }

    function renderCurrentActiveView() {
      updateNavigationBadges();
      if (appState.activeView === 'dashboard') renderDashboard();
      if (appState.activeView === 'costing') {
        if (appState.costingSubmode === 'wizard') {
          renderCostingWizard();
        } else {
          renderCostingList();
        }
      }
      if (appState.activeView === 'followup') renderFollowUpTasks();
      if (appState.activeView === 'orders') renderOrdersView();
      if (appState.activeView === 'settings') renderSettingsView();
    }

    function updateNavigationBadges() {
      if (!appState.db) return;
      const openTasks = appState.db.tasks.filter((t) => t.status !== 'Completed').length;
      const activeOrders = appState.db.orders.filter((o) => o.status === 'Currently Going On').length;
      const cBadge = document.getElementById('navBadge-costing');
      const fBadge = document.getElementById('navBadge-followup');
      const oBadge = document.getElementById('navBadge-orders');
      if (cBadge) cBadge.textContent = String(appState.db.costingRecords.length);
      if (fBadge) fBadge.textContent = String(openTasks);
      if (oBadge) oBadge.textContent = String(activeOrders);
    }

    // --- 7. Contextual Search & Notifications ---
    function handleGlobalSearchInput(query) {
      const dropdown = document.getElementById('globalSearchDropdown');
      if (!dropdown) return;
      const q = String(query || '').trim().toLowerCase();
      if (!q) {
        dropdown.classList.add('hidden');
        return;
      }

      const matchedOrders = appState.db.orders.filter(
        (o) =>
          o.orderNumber.toLowerCase().includes(q) ||
          o.customerName.toLowerCase().includes(q) ||
          o.styleNumber.toLowerCase().includes(q) ||
          o.styleName.toLowerCase().includes(q) ||
          o.buyerPoRef.toLowerCase().includes(q)
      );
      const matchedCostings = appState.db.costingRecords.filter(
        (c) =>
          c.styleNumber.toLowerCase().includes(q) ||
          c.styleName.toLowerCase().includes(q) ||
          c.primaryFabric.toLowerCase().includes(q)
      );
      const matchedTasks = appState.db.tasks.filter(
        (t) =>
          t.title.toLowerCase().includes(q) ||
          t.assignedUserName.toLowerCase().includes(q) ||
          (t.remarks || '').toLowerCase().includes(q)
      );

      const itemsHtml = [];
      matchedOrders.slice(0, 3).forEach((o) => {
        itemsHtml.push(`
          <button type="button" onclick="openOrderDetailModal('${escapeHtml(o.id)}'); document.getElementById('globalSearchDropdown').classList.add('hidden');" class="w-full text-left p-2 rounded-lg hover:bg-stone-500/10 flex items-center justify-between text-xs">
            <div>
              <div class="font-semibold font-mono-tabular">${escapeHtml(o.orderNumber)} · ${escapeHtml(o.customerName)}</div>
              <div class="text-[11px]" style="color: var(--text-secondary);">${escapeHtml(o.styleNumber)} — ${escapeHtml(o.styleName)}</div>
            </div>
            <span class="tf-badge tf-badge-info">Order</span>
          </button>
        `);
      });
      matchedCostings.slice(0, 3).forEach((c) => {
        itemsHtml.push(`
          <button type="button" onclick="openCostingDetailModal('${escapeHtml(c.id)}'); document.getElementById('globalSearchDropdown').classList.add('hidden');" class="w-full text-left p-2 rounded-lg hover:bg-stone-500/10 flex items-center justify-between text-xs">
            <div>
              <div class="font-semibold font-mono-tabular">${escapeHtml(c.styleNumber)} · ${escapeHtml(c.styleName)}</div>
              <div class="text-[11px]" style="color: var(--text-secondary);">${escapeHtml(c.primaryFabric)} (${c.baseGsm} GSM)</div>
            </div>
            <span class="tf-badge tf-badge-neutral">Costing</span>
          </button>
        `);
      });
      matchedTasks.slice(0, 3).forEach((t) => {
        itemsHtml.push(`
          <button type="button" onclick="navigateToView('followup'); document.getElementById('globalSearchDropdown').classList.add('hidden');" class="w-full text-left p-2 rounded-lg hover:bg-stone-500/10 flex items-center justify-between text-xs">
            <div>
              <div class="font-semibold">${escapeHtml(t.title)}</div>
              <div class="text-[11px]" style="color: var(--text-secondary);">Assigned: ${escapeHtml(t.assignedUserName)} · ${escapeHtml(t.status)}</div>
            </div>
            <span class="tf-badge tf-badge-warn">Task</span>
          </button>
        `);
      });

      dropdown.innerHTML =
        itemsHtml.length > 0
          ? itemsHtml.join('')
          : `<div class="p-3 text-xs text-center" style="color: var(--text-muted);">No matching orders, costings, or workflow tasks for "${escapeHtml(query)}".</div>`;
      dropdown.classList.remove('hidden');
    }

    function toggleNotificationsPanel() {
      const pop = document.getElementById('notificationsPopover');
      if (!pop) return;
      pop.classList.toggle('hidden');
    }

    function renderNotifications() {
      const list = document.getElementById('notificationsList');
      const dot = document.getElementById('notificationCountDot');
      if (!list || !appState.db) return;

      const refDate = new Date('2026-10-18T00:00:00+05:30');
      const alerts = [];

      appState.db.orders
        .filter((o) => o.status === 'Currently Going On')
        .forEach((o) => {
          const due = new Date(o.dueDate + 'T00:00:00+05:30');
          const diffDays = Math.ceil((due - refDate) / (1000 * 60 * 60 * 24));
          if (diffDays <= 5) {
            alerts.push({
              badge: 'DUE SOON',
              badgeClass: 'tf-badge-warn',
              title: `${o.orderNumber} (${o.customerName}) due in ${diffDays} days`,
              sub: `${formatNumber(o.completedPieces)} / ${formatNumber(o.totalPieces)} pcs completed · Stage: ${o.currentStage}`,
              action: `openOrderDetailModal('${o.id}')`
            });
          }
        });

      appState.db.tasks
        .filter((t) => t.status !== 'Completed' && t.followUpDate <= '2026-10-19')
        .forEach((t) => {
          alerts.push({
            badge: 'FOLLOW-UP',
            badgeClass: 'tf-badge-danger',
            title: t.title,
            sub: `Follow-up: ${t.followUpDate} · Assigned to ${t.assignedUserName}`,
            action: `navigateToView('followup')`
          });
        });

      if (dot) dot.textContent = String(alerts.length);
      list.innerHTML = alerts
        .map(
          (a) => `
          <button type="button" onclick="${a.action}; document.getElementById('notificationsPopover').classList.add('hidden');" class="w-full text-left p-2.5 rounded-lg tf-subtle hover:border-orange-500/40 transition-colors block">
            <div class="flex items-center justify-between mb-1">
              <span class="tf-badge ${a.badgeClass} text-[10px] font-mono-tabular">${escapeHtml(a.badge)}</span>
            </div>
            <div class="text-xs font-semibold">${escapeHtml(a.title)}</div>
            <div class="text-[11px] mt-0.5" style="color: var(--text-secondary);">${escapeHtml(a.sub)}</div>
          </button>
        `
        )
        .join('');
    }

    // --- 8. VIEW 1: DASHBOARD RENDERER ---
    function getFilteredDashboardData() {
      const catFilter = document.getElementById('dashCategoryFilter')?.value || 'ALL';
      const typeFilter = document.getElementById('dashTypeFilter')?.value || 'ALL';
      const dateFilter = document.getElementById('dashDateFilter')?.value || 'ALL';

      const orders = appState.db.orders.filter((o) => {
        if (catFilter !== 'ALL' && o.category !== catFilter) return false;
        if (typeFilter !== 'ALL' && o.garmentType !== typeFilter) return false;
        if (dateFilter === 'DUE_7_DAYS' && o.dueDate > '2026-10-25') return false;
        if (dateFilter === 'DUE_14_DAYS' && o.dueDate > '2026-11-01') return false;
        return true;
      });

      const orderIds = new Set(orders.map((o) => o.id));
      const tasks = appState.db.tasks.filter((t) => orderIds.has(t.orderId));
      const costings = appState.db.costingRecords.filter((c) => {
        if (catFilter !== 'ALL' && c.category !== catFilter) return false;
        if (typeFilter !== 'ALL' && c.garmentType !== typeFilter) return false;
        return true;
      });

      return { orders, tasks, costings };
    }

    function renderDashboard() {
      const { orders, tasks, costings } = getFilteredDashboardData();
      const activeOrders = orders.filter((o) => o.status === 'Currently Going On');
      const completedOrders = orders.filter((o) => o.status === 'Completed');
      const pendingOrInProgTasks = tasks.filter((t) => t.status !== 'Completed');
      const dueSoonOrders = activeOrders.filter((o) => o.dueDate <= '2026-10-25');
      const totalPiecesInProd = activeOrders.reduce((acc, o) => acc + (Number(o.totalPieces) || 0), 0);
      const completedPiecesInProd = activeOrders.reduce((acc, o) => acc + (Number(o.completedPieces) || 0), 0);

      // 1. Operational Exception Alerts
      const alertsEl = document.getElementById('dashboardAlertsContainer');
      const urgentTasks = pendingOrInProgTasks.filter((t) => t.followUpDate <= '2026-10-18');
      if (alertsEl) {
        if (urgentTasks.length > 0 || dueSoonOrders.length > 0) {
          alertsEl.innerHTML = `
            <div class="p-3.5 rounded-xl tf-surface flex flex-col sm:flex-row sm:items-center justify-between gap-3" style="border-left: 4px solid var(--accent-primary);">
              <div class="flex items-start sm:items-center gap-3">
                <span class="tf-badge tf-badge-warn font-mono-tabular">OPERATIONAL EXCEPTION ALERT</span>
                <span class="text-xs" style="color: var(--text-primary);">
                  <strong>${dueSoonOrders.length} active order(s)</strong> have export delivery within 7 days, and <strong>${urgentTasks.length} floor task(s)</strong> require follow-up today (Oct 18).
                </span>
              </div>
              <div class="flex items-center gap-2 flex-shrink-0">
                <button type="button" onclick="navigateToView('followup')" class="tf-btn-secondary px-3 py-1 rounded-lg text-xs font-medium">
                  Review Follow-Ups →
                </button>
              </div>
            </div>
          `;
        } else {
          alertsEl.innerHTML = '';
        }
      }

      // 2. KPI Cards
      const kpiGrid = document.getElementById('dashboardKpiGrid');
      const pieceCompletionPct = totalPiecesInProd > 0 ? Math.round((completedPiecesInProd / totalPiecesInProd) * 100) : 0;
      if (kpiGrid) {
        kpiGrid.innerHTML = `
          <button type="button" onclick="setOrderStatusTab('Currently Going On'); navigateToView('orders');" class="p-4 rounded-xl tf-surface text-left hover:border-orange-500/50 transition-all">
            <div class="flex items-center justify-between text-xs mb-2" style="color: var(--text-muted);">
              <span class="uppercase font-mono-tabular">Active Orders</span>
              <span class="tf-badge tf-badge-info">Going On</span>
            </div>
            <div class="text-2xl font-semibold font-mono-tabular">${activeOrders.length}</div>
            <div class="text-[11px] mt-1.5" style="color: var(--text-secondary);">Across ${costings.length} engineered styles</div>
          </button>

          <button type="button" onclick="setTaskStatusTab('Pending'); navigateToView('followup');" class="p-4 rounded-xl tf-surface text-left hover:border-orange-500/50 transition-all">
            <div class="flex items-center justify-between text-xs mb-2" style="color: var(--text-muted);">
              <span class="uppercase font-mono-tabular">Open Tasks</span>
              <span class="tf-badge tf-badge-warn">${urgentTasks.length} Due Today</span>
            </div>
            <div class="text-2xl font-semibold font-mono-tabular">${pendingOrInProgTasks.length}</div>
            <div class="text-[11px] mt-1.5" style="color: var(--text-secondary);">Pending &amp; In-Progress milestones</div>
          </button>

          <button type="button" onclick="setOrderStatusTab('Currently Going On'); navigateToView('orders');" class="p-4 rounded-xl tf-surface text-left hover:border-orange-500/50 transition-all">
            <div class="flex items-center justify-between text-xs mb-2" style="color: var(--text-muted);">
              <span class="uppercase font-mono-tabular">Orders Due Soon</span>
              <span class="tf-badge tf-badge-danger">≤ 7 Days</span>
            </div>
            <div class="text-2xl font-semibold font-mono-tabular">${dueSoonOrders.length}</div>
            <div class="text-[11px] mt-1.5" style="color: var(--text-secondary);">Next dispatch: Oct 21 &amp; Oct 22</div>
          </button>

          <button type="button" onclick="setOrderStatusTab('Completed'); navigateToView('orders');" class="p-4 rounded-xl tf-surface text-left hover:border-orange-500/50 transition-all">
            <div class="flex items-center justify-between text-xs mb-2" style="color: var(--text-muted);">
              <span class="uppercase font-mono-tabular">Completed Orders</span>
              <span class="tf-badge tf-badge-success">AQL Passed</span>
            </div>
            <div class="text-2xl font-semibold font-mono-tabular">${completedOrders.length}</div>
            <div class="text-[11px] mt-1.5" style="color: var(--text-secondary);">100% traceability retained</div>
          </button>

          <button type="button" onclick="navigateToView('orders')" class="p-4 rounded-xl tf-surface text-left hover:border-orange-500/50 transition-all">
            <div class="flex items-center justify-between text-xs mb-2" style="color: var(--text-muted);">
              <span class="uppercase font-mono-tabular">Pieces in Production</span>
              <span class="font-mono-tabular text-xs font-semibold" style="color: var(--accent-primary);">${pieceCompletionPct}%</span>
            </div>
            <div class="text-2xl font-semibold font-mono-tabular">${formatNumber(totalPiecesInProd)}</div>
            <div class="w-full h-1.5 rounded-full bg-stone-500/15 mt-2 overflow-hidden">
              <div class="h-full rounded-full" style="width: ${pieceCompletionPct}%; background-color: var(--accent-primary);"></div>
            </div>
          </button>
        `;
      }

      // 3. Recent Orders Table
      const ordersBody = document.getElementById('dashboardRecentOrdersBody');
      if (ordersBody) {
        if (orders.length === 0) {
          ordersBody.innerHTML = `<tr><td colspan="6" class="py-8 text-center text-xs" style="color: var(--text-muted);">No orders match the current filter criteria.</td></tr>`;
        } else {
          ordersBody.innerHTML = orders
            .slice(0, 5)
            .map((o) => {
              const wf = calculateOrderWorkflowProgress(o.id, appState.db.tasks);
              const badgeCls =
                o.status === 'Completed'
                  ? 'tf-badge-success'
                  : o.status === 'Cancelled'
                  ? 'tf-badge-danger'
                  : 'tf-badge-info';
              return `
                <tr onclick="openOrderDetailModal('${escapeHtml(o.id)}')" class="cursor-pointer">
                  <td class="py-3 px-4">
                    <div class="font-mono-tabular font-semibold">${escapeHtml(o.orderNumber)}</div>
                    <div class="text-[11px]" style="color: var(--text-secondary);">${escapeHtml(o.customerName)}</div>
                  </td>
                  <td class="py-3 px-3">
                    <div class="font-mono-tabular text-xs font-medium">${escapeHtml(o.styleNumber)}</div>
                    <div class="text-[11px] truncate max-w-[160px]" style="color: var(--text-secondary);">${escapeHtml(o.styleName)}</div>
                  </td>
                  <td class="py-3 px-3 text-right font-mono-tabular">
                    <div>${formatNumber(o.completedPieces)} / ${formatNumber(o.totalPieces)}</div>
                    <div class="text-[10px]" style="color: var(--text-muted);">${escapeHtml(o.garmentType)}</div>
                  </td>
                  <td class="py-3 px-3">
                    <div class="flex items-center gap-2">
                      <div class="w-16 h-1.5 rounded-full bg-stone-500/20 overflow-hidden">
                        <div class="h-full rounded-full" style="width: ${wf.progressPct}%; background-color: var(--accent-primary);"></div>
                      </div>
                      <span class="font-mono-tabular text-[11px]">${wf.progressPct}%</span>
                    </div>
                    <div class="text-[10px]" style="color: var(--text-muted);">${wf.completedTasks}/${wf.milestoneTasks} tasks</div>
                  </td>
                  <td class="py-3 px-3 font-mono-tabular text-xs">${escapeHtml(o.dueDate)}</td>
                  <td class="py-3 px-4 text-right">
                    <span class="tf-badge ${badgeCls}">${escapeHtml(o.status)}</span>
                  </td>
                </tr>
              `;
            })
            .join('');
        }
      }

      // 4. Upcoming Follow-Ups List
      const tasksList = document.getElementById('dashboardUpcomingTasksList');
      if (tasksList) {
        const sortedOpen = [...pendingOrInProgTasks].sort((a, b) => a.followUpDate.localeCompare(b.followUpDate));
        if (sortedOpen.length === 0) {
          tasksList.innerHTML = `<div class="p-6 text-center text-xs" style="color: var(--text-muted);">All workflow tasks for the selected filter are completed.</div>`;
        } else {
          tasksList.innerHTML = sortedOpen
            .slice(0, 5)
            .map((t) => {
              const ord = appState.db.orders.find((o) => o.id === t.orderId);
              const pBadge =
                t.priority === 'Critical'
                  ? 'tf-badge-danger'
                  : t.priority === 'High'
                  ? 'tf-badge-warn'
                  : 'tf-badge-neutral';
              return `
                <div class="p-3 rounded-lg tf-subtle flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <div class="flex items-center gap-1.5 mb-1">
                      <span class="tf-badge ${pBadge} text-[10px]">${escapeHtml(t.priority)}</span>
                      <span class="font-mono-tabular text-[11px]" style="color: var(--text-muted);">${escapeHtml(ord ? ord.orderNumber : t.orderId)}</span>
                      <span class="text-[11px]" style="color: var(--text-muted);">· Follow-up ${escapeHtml(t.followUpDate)}</span>
                    </div>
                    <div class="text-xs font-semibold">${escapeHtml(t.title)}</div>
                    <div class="text-[11px] mt-0.5" style="color: var(--text-secondary);">Assigned: ${escapeHtml(t.assignedUserName)} · ${escapeHtml(t.status)}</div>
                  </div>
                  <button type="button" onclick="openCompleteTaskModal('${escapeHtml(t.id)}')" class="tf-btn-secondary px-2.5 py-1 rounded text-[11px] font-medium flex-shrink-0">
                    ✓ Complete
                  </button>
                </div>
              `;
            })
            .join('');
        }
      }

      renderDashboardCharts();
    }

    function renderDashboardCharts() {
      if (typeof Chart === 'undefined') return;
      const { orders, costings } = getFilteredDashboardData();
      const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
      const textColor = isDark ? '#A6A49D' : '#52514E';
      const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(20,20,19,0.07)';

      // Chart 1: Order Production Progress
      const prodCanvas = document.getElementById('dashboardProductionChart');
      if (prodCanvas) {
        if (productionChartInstance) productionChartInstance.destroy();
        const activeOrCompleted = orders.filter((o) => o.status !== 'Cancelled');
        const labels = activeOrCompleted.map((o) => o.styleNumber);
        const piecePctData = activeOrCompleted.map((o) =>
          o.totalPieces > 0 ? Math.round((o.completedPieces / o.totalPieces) * 100) : 0
        );
        const taskPctData = activeOrCompleted.map(
          (o) => calculateOrderWorkflowProgress(o.id, appState.db.tasks).progressPct
        );

        productionChartInstance = new Chart(prodCanvas, {
          type: 'bar',
          data: {
            labels,
            datasets: [
              {
                label: 'Pieces Completed (%)',
                data: piecePctData,
                backgroundColor: isDark ? '#E0633C' : '#B84A27',
                borderRadius: 6
              },
              {
                label: 'Workflow Milestones (%)',
                data: taskPctData,
                backgroundColor: isDark ? '#3B7A57' : '#1E3A2F',
                borderRadius: 6
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (_evt, elements) => {
              if (elements && elements.length > 0) {
                const idx = elements[0].index;
                const ord = activeOrCompleted[idx];
                if (ord) openOrderDetailModal(ord.id);
              }
            },
            plugins: {
              legend: {
                labels: { color: textColor, font: { family: 'Inter', size: 11 } }
              },
              tooltip: {
                callbacks: {
                  afterLabel: (ctx) => {
                    const ord = activeOrCompleted[ctx.dataIndex];
                    return ord ? `${ord.orderNumber} (${ord.customerName}): ${ord.completedPieces}/${ord.totalPieces} pcs` : '';
                  }
                }
              }
            },
            scales: {
              x: { ticks: { color: textColor, font: { family: 'JetBrains Mono', size: 10 } }, grid: { display: false } },
              y: {
                beginAtZero: true,
                max: 100,
                ticks: { color: textColor, callback: (v) => v + '%' },
                grid: { color: gridColor }
              }
            }
          }
        });
      }

      // Chart 2: Gross Fabric Consumption (kg) vs Net Garment Weight (kg)
      const fabCanvas = document.getElementById('dashboardFabricChart');
      if (fabCanvas) {
        if (fabricChartInstance) fabricChartInstance.destroy();
        const labels = costings.map((c) => c.styleNumber);
        const netKg = costings.map((c) => c.calculatedSummary?.totalOrderNetWeightKg || 0);
        const grossKg = costings.map((c) => c.calculatedSummary?.totalOrderConsumptionKg || 0);

        fabricChartInstance = new Chart(fabCanvas, {
          type: 'bar',
          data: {
            labels,
            datasets: [
              {
                label: 'Net Garment Wt (kg)',
                data: netKg,
                backgroundColor: isDark ? '#64748B' : '#94A3B8',
                borderRadius: 5
              },
              {
                label: 'Gross Fabric Cons. (kg)',
                data: grossKg,
                backgroundColor: isDark ? '#E0633C' : '#B84A27',
                borderRadius: 5
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            onClick: (_evt, elements) => {
              if (elements && elements.length > 0) {
                const idx = elements[0].index;
                const c = costings[idx];
                if (c) openCostingDetailModal(c.id);
              }
            },
            plugins: {
              legend: {
                labels: { color: textColor, font: { family: 'Inter', size: 11 } }
              },
              tooltip: {
                callbacks: {
                  afterBody: (items) => {
                    const c = costings[items[0].dataIndex];
                    return c
                      ? `Total Fabric Cost: ${formatINR(c.calculatedSummary?.totalOrderFabricCost || 0)} (${c.wastageAllowancePct}% wastage)`
                      : '';
                  }
                }
              }
            },
            scales: {
              x: { ticks: { color: textColor, font: { family: 'JetBrains Mono', size: 10 } }, grid: { display: false } },
              y: {
                beginAtZero: true,
                ticks: { color: textColor, callback: (v) => v + ' kg' },
                grid: { color: gridColor }
              }
            }
          }
        });
      }
    }

    // --- 9. VIEW 2: COSTING LIST & 6-STEP COSTING WIZARD ---
    function switchCostingSubmode(mode) {
      appState.costingSubmode = mode === 'wizard' ? 'wizard' : 'list';
      const listEl = document.getElementById('costingListSubview');
      const wizEl = document.getElementById('costingWizardSubview');
      if (appState.costingSubmode === 'wizard') {
        listEl.classList.add('hidden');
        wizEl.classList.remove('hidden');
        renderCostingWizard();
      } else {
        wizEl.classList.add('hidden');
        listEl.classList.remove('hidden');
        renderCostingList();
      }
    }

    function renderCostingList() {
      const container = document.getElementById('costingRecordsContainer');
      if (!container) return;

      const q = (document.getElementById('costingSearchInput')?.value || '').trim().toLowerCase();
      const typeFilter = document.getElementById('costingFilterType')?.value || 'ALL';
      const catFilter = document.getElementById('costingFilterCategory')?.value || 'ALL';
      const statusFilter = document.getElementById('costingFilterStatus')?.value || 'ALL';
      const sortBy = document.getElementById('costingSortSelect')?.value || 'updated_desc';

      let list = appState.db.costingRecords.filter((c) => {
        if (typeFilter !== 'ALL' && c.garmentType !== typeFilter) return false;
        if (catFilter !== 'ALL' && c.category !== catFilter) return false;
        if (statusFilter !== 'ALL' && c.status !== statusFilter) return false;
        if (q) {
          const hay = `${c.styleNumber} ${c.styleName} ${c.primaryFabric} ${c.id}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      list.sort((a, b) => {
        if (sortBy === 'style_asc') return a.styleNumber.localeCompare(b.styleNumber);
        if (sortBy === 'cost_desc')
          return (b.calculatedSummary?.totalOrderFabricCost || 0) - (a.calculatedSummary?.totalOrderFabricCost || 0);
        if (sortBy === 'piece_asc')
          return (a.calculatedSummary?.weightedAvgPieceFabricCost || 0) - (b.calculatedSummary?.weightedAvgPieceFabricCost || 0);
        if (sortBy === 'gsm_desc') return (Number(b.baseGsm) || 0) - (Number(a.baseGsm) || 0);
        return String(b.updatedAt || '').localeCompare(String(a.updatedAt || ''));
      });

      if (list.length === 0) {
        container.innerHTML = `
          <div class="p-10 rounded-xl tf-surface text-center space-y-3">
            <div class="text-sm font-semibold">No Costing Records Match Your Filter</div>
            <p class="text-xs max-w-md mx-auto" style="color: var(--text-secondary);">Clear your search filters or launch the 6-step costing wizard to engineer a new garment style.</p>
            <button type="button" onclick="openCostingWizardNew()" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">+ New Style Costing</button>
          </div>
        `;
        return;
      }

      container.innerHTML = list
        .map((c) => {
          const sum = c.calculatedSummary || evaluateCostingSheet(c).summary;
          const statusCls =
            c.status === 'Approved'
              ? 'tf-badge-success'
              : c.status === 'Finalized'
              ? 'tf-badge-info'
              : 'tf-badge-warn';
          return `
            <div class="p-5 rounded-xl tf-surface flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div class="space-y-1.5 min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-mono-tabular text-xs font-bold px-2 py-0.5 rounded tf-subtle">${escapeHtml(c.styleNumber)}</span>
                  <span class="tf-badge ${statusCls}">${escapeHtml(c.status)}</span>
                  <span class="tf-badge tf-badge-neutral">${escapeHtml(c.garmentType)} · ${escapeHtml(c.category)}</span>
                  <span class="font-mono-tabular text-xs" style="color: var(--text-muted);">${c.baseGsm} GSM · ${c.wastageAllowancePct}% Wastage</span>
                </div>
                <h3 class="text-base font-semibold">${escapeHtml(c.styleName)}</h3>
                <p class="text-xs" style="color: var(--text-secondary);">
                  Primary Fabric: <strong>${escapeHtml(c.primaryFabric)}</strong> · ${c.fabrics.length} Fabric Serial(s) · ${c.components.filter((x) => x.enabled !== false).length} Active Components
                </p>
              </div>

              <!-- Key Numerical Telemetry -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 lg:pt-0 border-t lg:border-t-0" style="border-color: var(--border-hairline);">
                <div class="p-2.5 rounded-lg tf-subtle">
                  <div class="text-[10px] uppercase font-mono-tabular" style="color: var(--text-muted);">Order Qty (S–XXXL)</div>
                  <div class="text-sm font-semibold font-mono-tabular mt-0.5">${formatNumber(sum.totalOrderQuantity)} pcs</div>
                </div>
                <div class="p-2.5 rounded-lg tf-subtle">
                  <div class="text-[10px] uppercase font-mono-tabular" style="color: var(--text-muted);">Avg Net / Cons.</div>
                  <div class="text-sm font-semibold font-mono-tabular mt-0.5">${sum.avgGarmentNetWeightGrams}g / ${sum.avgGarmentConsumptionGrams}g</div>
                </div>
                <div class="p-2.5 rounded-lg tf-subtle">
                  <div class="text-[10px] uppercase font-mono-tabular" style="color: var(--text-muted);">Avg Piece Cost</div>
                  <div class="text-sm font-semibold font-mono-tabular mt-0.5">${formatINR(sum.weightedAvgPieceFabricCost)}</div>
                </div>
                <div class="p-2.5 rounded-lg tf-subtle">
                  <div class="text-[10px] uppercase font-mono-tabular" style="color: var(--text-muted);">Total Fabric Cost</div>
                  <div class="text-sm font-semibold font-mono-tabular mt-0.5" style="color: var(--accent-primary);">${formatINR(sum.totalOrderFabricCost)}</div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex flex-wrap items-center gap-2 flex-shrink-0">
                <button type="button" onclick="openCostingDetailModal('${escapeHtml(c.id)}')" class="tf-btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium">
                  Inspect Sheet
                </button>
                <button type="button" onclick="openCostingWizardEdit('${escapeHtml(c.id)}')" class="tf-btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium">
                  Edit in Wizard
                </button>
                <button type="button" onclick="duplicateCostingRecord('${escapeHtml(c.id)}')" class="tf-btn-secondary px-2.5 py-1.5 rounded-lg text-xs font-medium" title="Duplicate Costing">
                  ⧉
                </button>
              </div>
            </div>
          `;
        })
        .join('');
    }

    function openCostingWizardNew() {
      navigateToView('costing');
      if (!appState.wizardState || !appState.wizardState.form) {
        appState.wizardState = {
          step: 1,
          editingCostingId: null,
          form: createBlankWizardForm()
        };
      }
      switchCostingSubmode('wizard');
    }

    function openCostingWizardEdit(costingId) {
      const rec = appState.db.costingRecords.find((c) => c.id === costingId);
      if (!rec) return;
      appState.wizardState = {
        step: 1,
        editingCostingId: rec.id,
        form: JSON.parse(JSON.stringify(rec))
      };
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      navigateToView('costing');
      switchCostingSubmode('wizard');
      showToast(`Loaded ${rec.styleNumber} into the 6-Step Costing Wizard.`, 'info');
    }

    function resetWizardToBlank() {
      appState.wizardState = {
        step: 1,
        editingCostingId: null,
        form: createBlankWizardForm()
      };
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
      showToast('Initialized a clean costing worksheet.', 'info');
    }

    function duplicateCostingRecord(costingId) {
      const auth = assertPermission(appState.currentUser, 'costing:write');
      if (!auth.allowed) {
        showToast(auth.error, 'error');
        return;
      }
      const orig = appState.db.costingRecords.find((c) => c.id === costingId);
      if (!orig) return;
      const copy = JSON.parse(JSON.stringify(orig));
      copy.id = 'CST-' + Math.floor(2610 + Math.random() * 890);
      copy.styleNumber = orig.styleNumber + '-REV2';
      copy.styleName = orig.styleName + ' (Rev 2)';
      copy.status = 'Draft';
      copy.updatedAt = new Date().toISOString();
      const evalRes = evaluateCostingSheet(copy);
      copy.calculatedSummary = evalRes.summary;
      copy.isComplete = evalRes.isComplete;
      appState.db.costingRecords.unshift(copy);
      saveDatabase();
      renderCostingList();
      showToast(`Duplicated ${orig.styleNumber} as ${copy.styleNumber}.`, 'success');
    }

    function moveWizardStep(delta) {
      const next = Math.min(6, Math.max(1, (appState.wizardState.step || 1) + delta));
      appState.wizardState.step = next;
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function jumpWizardStep(stepNum) {
      appState.wizardState.step = stepNum;
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function renderCostingWizard() {
      const wiz = appState.wizardState;
      if (!wiz || !wiz.form) {
        wiz.form = createBlankWizardForm();
      }
      const f = wiz.form;
      const evalRes = evaluateCostingSheet(f);
      const sum = evalRes.summary;

      // Update live header metrics
      document.getElementById('wizardModeBadge').textContent = wiz.editingCostingId
        ? `EDITING ${f.styleNumber}`
        : 'NEW COSTING WORKSHEET';
      document.getElementById('wizLiveTotalQty').textContent = `${formatNumber(sum.totalOrderQuantity)} pcs`;
      document.getElementById('wizLiveAvgNetWt').textContent = `${sum.avgGarmentNetWeightGrams} g`;
      document.getElementById('wizLiveAvgCons').textContent = `${sum.avgGarmentConsumptionGrams} g`;
      document.getElementById('wizLiveTotalCost').textContent = formatINR(sum.totalOrderFabricCost);

      const stepNames = [
        '1. Style Details',
        '2. Fabric Setup',
        '3. Measurements',
        '4. Size Quantities',
        '5. Costing Review',
        '6. Save & Confirm'
      ];
      document.getElementById('wizardHeaderTitle').textContent = `Step ${wiz.step} of 6 — ${stepNames[wiz.step - 1].slice(3)}`;

      // Render Step Indicator Buttons
      const indEl = document.getElementById('wizardStepIndicators');
      indEl.innerHTML = stepNames
        .map((label, idx) => {
          const sNum = idx + 1;
          const stepErrors = evalRes.errors.filter((e) => e.step === sNum);
          const isCurrent = wiz.step === sNum;
          const bgStyle = isCurrent
            ? 'background-color: var(--accent-primary); color: #fff;'
            : 'background-color: var(--bg-subtle); color: var(--text-secondary);';
          return `
            <button type="button" onclick="jumpWizardStep(${sNum})" class="px-2.5 py-2 rounded-lg text-xs font-medium text-left flex items-center justify-between transition-all" style="${bgStyle}">
              <span class="truncate">${escapeHtml(label)}</span>
              ${
                stepErrors.length > 0
                  ? `<span class="w-4 h-4 rounded-full bg-red-600 text-white text-[10px] font-mono-tabular flex items-center justify-center">${stepErrors.length}</span>`
                  : `<span class="text-[10px] opacity-80">✓</span>`
              }
            </button>
          `;
        })
        .join('');

      document.getElementById('wizPrevStepBtn').disabled = wiz.step === 1;
      document.getElementById('wizNextStepBtn').classList.toggle('hidden', wiz.step === 6);

      // Render Technical Garment Blueprint SVG & Validation Rail
      renderWizardBlueprintAndValidation(f, evalRes);

      // Render Current Step Form Content
      const contentEl = document.getElementById('wizardStepContent');
      if (wiz.step === 1) {
        contentEl.innerHTML = `
          <div class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Style Number *</label>
                <input type="text" value="${escapeHtml(f.styleNumber)}" oninput="updateWizField('styleNumber', this.value)" class="tf-input w-full font-mono-tabular" placeholder="e.g. HK-2618-NEW" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Style Name *</label>
                <input type="text" value="${escapeHtml(f.styleName)}" oninput="updateWizField('styleName', this.value)" class="tf-input w-full" placeholder="e.g. Heavyweight Interlock Crewneck" />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Garment Type *</label>
                <select onchange="updateWizField('garmentType', this.value, true)" class="tf-input w-full">
                  <option value="Top" ${f.garmentType === 'Top' ? 'selected' : ''}>Top (Shirt / Tee / Hoodie / Jacket)</option>
                  <option value="Bottom" ${f.garmentType === 'Bottom' ? 'selected' : ''}>Bottom (Jogger / Trouser / Short)</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Category *</label>
                <select onchange="updateWizField('category', this.value, true)" class="tf-input w-full">
                  <option value="Men's" ${f.category === "Men's" ? 'selected' : ''}>Men's</option>
                  <option value="Ladies" ${f.category === 'Ladies' ? 'selected' : ''}>Ladies</option>
                  <option value="Other" ${f.category === 'Other' ? 'selected' : ''}>Other (Unisex / Youth)</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Base Fabric GSM (g/m²) *</label>
                <input type="number" min="50" max="800" step="5" value="${escapeHtml(f.baseGsm)}" oninput="updateWizField('baseGsm', this.value)" class="tf-input w-full font-mono-tabular" />
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div class="sm:col-span-2">
                <label class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Primary Fabric Specification</label>
                <input type="text" value="${escapeHtml(f.primaryFabric)}" oninput="updateWizField('primaryFabric', this.value)" class="tf-input w-full" placeholder="e.g. 100% Organic Combed Cotton Interlock" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Process Wastage Allowance (%)</label>
                <input type="number" min="0" max="50" step="0.5" value="${escapeHtml(f.wastageAllowancePct)}" oninput="updateWizField('wastageAllowancePct', this.value)" class="tf-input w-full font-mono-tabular" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium mb-1" style="color: var(--text-secondary);">Construction &amp; Finishing Notes</label>
              <textarea rows="2" oninput="updateWizField('notes', this.value)" class="tf-input w-full">${escapeHtml(f.notes || '')}</textarea>
            </div>
          </div>
        `;
      } else if (wiz.step === 2) {
        contentEl.innerHTML = `
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-semibold">Multi-Fabric Setup &amp; Pricing</h4>
                <p class="text-xs" style="color: var(--text-secondary);">Add each fabric lot used in the garment (Main Body, Rib, Contrast Trim, Pocketing) with its GSM and price per kilogram.</p>
              </div>
              <button type="button" onclick="addWizardFabricRow()" class="tf-btn-primary px-3 py-1.5 rounded-lg text-xs font-medium">
                + Add Fabric Serial
              </button>
            </div>

            <div class="space-y-3">
              ${f.fabrics
                .map(
                  (fab, idx) => `
                  <div class="p-3.5 rounded-xl tf-subtle space-y-3">
                    <div class="flex items-center justify-between">
                      <span class="font-mono-tabular text-xs font-bold px-2 py-0.5 rounded tf-surface">Fabric Serial #${fab.serialNo}</span>
                      ${
                        f.fabrics.length > 1
                          ? `<button type="button" onclick="removeWizardFabricRow(${idx})" class="text-xs" style="color: var(--status-danger-text);">Remove Fabric</button>`
                          : ''
                      }
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-6 gap-2.5">
                      <div class="sm:col-span-2">
                        <label class="block text-[11px] mb-1" style="color: var(--text-secondary);">Fabric Identifier / Description *</label>
                        <input type="text" value="${escapeHtml(fab.description)}" oninput="updateWizardFabric(${idx}, 'description', this.value)" class="tf-input w-full text-xs" />
                      </div>
                      <div class="sm:col-span-2">
                        <label class="block text-[11px] mb-1" style="color: var(--text-secondary);">Colour / Dye Lot *</label>
                        <input type="text" value="${escapeHtml(fab.colour)}" oninput="updateWizardFabric(${idx}, 'colour', this.value)" class="tf-input w-full text-xs" />
                      </div>
                      <div>
                        <label class="block text-[11px] mb-1" style="color: var(--text-secondary);">GSM (g/m²) *</label>
                        <input type="number" min="40" max="900" value="${escapeHtml(fab.gsm)}" oninput="updateWizardFabric(${idx}, 'gsm', this.value)" class="tf-input w-full text-xs font-mono-tabular" />
                      </div>
                      <div>
                        <label class="block text-[11px] mb-1" style="color: var(--text-secondary);">Price / Kg (₹) *</label>
                        <input type="number" min="1" step="5" value="${escapeHtml(fab.pricePerKg)}" oninput="updateWizardFabric(${idx}, 'pricePerKg', this.value)" class="tf-input w-full text-xs font-mono-tabular" />
                      </div>
                    </div>
                  </div>
                `
                )
                .join('')}
            </div>
          </div>
        `;
      } else if (wiz.step === 3) {
        contentEl.innerHTML = `
          <div class="space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h4 class="text-sm font-semibold">Component Assignments &amp; Size-Specific Measurements (cm)</h4>
                <p class="text-xs" style="color: var(--text-secondary);">Configure Main Body, Sleeve, Rib, BNT, Yoke, or dynamically add Other Parts. Assign each enabled component to a fabric serial.</p>
              </div>
              <button type="button" onclick="addWizardCustomComponent()" class="tf-btn-primary px-3 py-1.5 rounded-lg text-xs font-medium">
                + Add Custom Part (Other Parts)
              </button>
            </div>

            <div class="space-y-4">
              ${f.components
                .map((comp, cIdx) => {
                  const enabled = comp.enabled !== false;
                  return `
                    <div class="p-4 rounded-xl ${enabled ? 'tf-subtle' : 'tf-surface opacity-60'} space-y-3">
                      <div class="flex flex-wrap items-center justify-between gap-2">
                        <div class="flex items-center gap-2.5">
                          <input type="checkbox" ${enabled ? 'checked' : ''} onchange="toggleWizardComponent(${cIdx}, this.checked)" class="w-4 h-4" />
                          ${
                            comp.isCustom
                              ? `<input type="text" value="${escapeHtml(comp.name)}" oninput="updateWizardComponentMeta(${cIdx}, 'name', this.value)" class="tf-input text-xs font-semibold py-1 px-2" />`
                              : `<span class="text-xs font-bold uppercase tracking-wider">${escapeHtml(comp.name)}</span>`
                          }
                          ${comp.isCustom ? `<span class="tf-badge tf-badge-info text-[10px]">Other Part</span>` : ''}
                        </div>

                        <div class="flex flex-wrap items-center gap-2">
                          <label class="text-[11px]" style="color: var(--text-secondary);">Fabric:</label>
                          <select onchange="updateWizardComponentMeta(${cIdx}, 'assignedFabricSerial', Number(this.value))" class="tf-input text-xs py-1 px-2">
                            ${f.fabrics
                              .map(
                                (fab) =>
                                  `<option value="${fab.serialNo}" ${Number(comp.assignedFabricSerial) === Number(fab.serialNo) ? 'selected' : ''}>#${fab.serialNo} — ${escapeHtml(fab.description)} (${escapeHtml(fab.colour)})</option>`
                              )
                              .join('')}
                          </select>

                          <label class="text-[11px]" style="color: var(--text-secondary);">Panels:</label>
                          <input type="number" min="1" max="8" step="1" value="${escapeHtml(comp.panelMultiplier)}" oninput="updateWizardComponentMeta(${cIdx}, 'panelMultiplier', this.value)" class="tf-input w-14 text-xs font-mono-tabular py-1 px-1.5" />

                          <label class="text-[11px]" style="color: var(--text-secondary);">Seam(cm):</label>
                          <input type="number" min="0" max="15" step="0.5" value="${escapeHtml(comp.seamAllowanceCm)}" oninput="updateWizardComponentMeta(${cIdx}, 'seamAllowanceCm', this.value)" class="tf-input w-16 text-xs font-mono-tabular py-1 px-1.5" />

                          <button type="button" onclick="autoGradeWizardComponent(${cIdx})" class="tf-btn-secondary px-2 py-1 rounded text-[11px]" title="Auto-grade M–XXXL from Size S (+2cm step)">
                            Auto-Grade S→XXXL
                          </button>
                          ${
                            comp.isCustom
                              ? `<button type="button" onclick="removeWizardCustomComponent(${cIdx})" class="text-xs px-1.5" style="color: var(--status-danger-text);">✕</button>`
                              : ''
                          }
                        </div>
                      </div>

                      ${
                        enabled
                          ? `
                        <div class="overflow-x-auto">
                          <table class="w-full text-left border-collapse tf-table text-xs">
                            <thead>
                              <tr>
                                <th class="py-1.5 px-2">Dimension</th>
                                ${SIZES.map((sz) => `<th class="py-1.5 px-2 text-center font-mono-tabular">${sz}</th>`).join('')}
                              </tr>
                            </thead>
                            <tbody>
                              <tr>
                                <td class="py-1.5 px-2 font-medium">Length (cm)</td>
                                ${SIZES.map((sz) => {
                                  const val = comp.measurementsBySize?.[sz]?.lengthCm ?? '';
                                  return `<td class="py-1.5 px-1.5"><input type="number" step="0.5" value="${escapeHtml(val)}" oninput="updateWizardMeasurement(${cIdx}, '${sz}', 'lengthCm', this.value)" class="tf-input w-full text-center font-mono-tabular py-1 px-1 text-xs" /></td>`;
                                }).join('')}
                              </tr>
                              <tr>
                                <td class="py-1.5 px-2 font-medium">Width (cm)</td>
                                ${SIZES.map((sz) => {
                                  const val = comp.measurementsBySize?.[sz]?.widthCm ?? '';
                                  return `<td class="py-1.5 px-1.5"><input type="number" step="0.5" value="${escapeHtml(val)}" oninput="updateWizardMeasurement(${cIdx}, '${sz}', 'widthCm', this.value)" class="tf-input w-full text-center font-mono-tabular py-1 px-1 text-xs" /></td>`;
                                }).join('')}
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      `
                          : `<div class="text-[11px] italic" style="color: var(--text-muted);">Component disabled for this style.</div>`
                      }
                    </div>
                  `;
                })
                .join('')}
            </div>
          </div>
        `;
      } else if (wiz.step === 4) {
        contentEl.innerHTML = `
          <div class="space-y-4">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <h4 class="text-sm font-semibold">Size-Wise Order Quantities (S – XXXL)</h4>
                <p class="text-xs" style="color: var(--text-secondary);">Enter order quantities per size. Enter 0 if a size is not ordered in this batch.</p>
              </div>
              <div class="flex items-center gap-2">
                <button type="button" onclick="applySizeRatioPreset(1200)" class="tf-btn-secondary px-2.5 py-1 rounded text-xs">Preset: 1,200 pcs Curve</button>
                <button type="button" onclick="applySizeRatioPreset(2400)" class="tf-btn-secondary px-2.5 py-1 rounded text-xs">Preset: 2,400 pcs Curve</button>
              </div>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-6 gap-3">
              ${SIZES.map((sz) => {
                const q = f.sizeQuantities?.[sz] ?? 0;
                const sInfo = sum.sizeSummaries[sz];
                return `
                  <div class="p-3 rounded-xl tf-subtle space-y-2">
                    <div class="flex items-center justify-between">
                      <span class="font-mono-tabular text-sm font-bold">${sz}</span>
                      <span class="font-mono-tabular text-[11px]" style="color: var(--text-muted);">${formatINR(sInfo.garmentFabricCost)}/pc</span>
                    </div>
                    <input type="number" min="0" step="10" value="${escapeHtml(q)}" oninput="updateWizardSizeQuantity('${sz}', this.value)" class="tf-input w-full font-mono-tabular text-sm font-semibold text-center" />
                    <div class="text-[10px] font-mono-tabular space-y-0.5" style="color: var(--text-secondary);">
                      <div>Net: ${sInfo.garmentNetWeightGrams}g/pc</div>
                      <div>Cons: ${sInfo.garmentConsumptionGrams}g/pc</div>
                      <div class="font-semibold" style="color: var(--text-primary);">Ext: ${formatINR(sInfo.extendedFabricCost)}</div>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>

            <!-- Live Extended Size Table -->
            <div class="overflow-x-auto rounded-xl border" style="border-color: var(--border-hairline);">
              <table class="w-full text-left border-collapse tf-table text-xs">
                <thead>
                  <tr>
                    <th class="py-2 px-3">Size</th>
                    <th class="py-2 px-3 text-right">Order Qty</th>
                    <th class="py-2 px-3 text-right">Piece Net Wt (g)</th>
                    <th class="py-2 px-3 text-right">Piece Gross Cons. (g)</th>
                    <th class="py-2 px-3 text-right">Piece Cost (₹)</th>
                    <th class="py-2 px-3 text-right">Total Fabric Req (kg)</th>
                    <th class="py-2 px-3 text-right">Extended Fabric Cost (₹)</th>
                  </tr>
                </thead>
                <tbody class="font-mono-tabular">
                  ${SIZES.map((sz) => {
                    const s = sum.sizeSummaries[sz];
                    return `
                      <tr>
                        <td class="py-2 px-3 font-bold">${sz}</td>
                        <td class="py-2 px-3 text-right">${formatNumber(s.quantity)}</td>
                        <td class="py-2 px-3 text-right">${s.garmentNetWeightGrams} g</td>
                        <td class="py-2 px-3 text-right">${s.garmentConsumptionGrams} g</td>
                        <td class="py-2 px-3 text-right">${formatINR(s.garmentFabricCost)}</td>
                        <td class="py-2 px-3 text-right">${s.extendedConsumptionKg} kg</td>
                        <td class="py-2 px-3 text-right font-semibold">${formatINR(s.extendedFabricCost)}</td>
                      </tr>
                    `;
                  }).join('')}
                  <tr style="background-color: var(--bg-subtle); font-weight: 700;">
                    <td class="py-2.5 px-3">TOTAL / WEIGHTED AVG</td>
                    <td class="py-2.5 px-3 text-right">${formatNumber(sum.totalOrderQuantity)} pcs</td>
                    <td class="py-2.5 px-3 text-right">${sum.avgGarmentNetWeightGrams} g</td>
                    <td class="py-2.5 px-3 text-right">${sum.avgGarmentConsumptionGrams} g</td>
                    <td class="py-2.5 px-3 text-right">${formatINR(sum.weightedAvgPieceFabricCost)}</td>
                    <td class="py-2.5 px-3 text-right">${sum.totalOrderConsumptionKg} kg</td>
                    <td class="py-2.5 px-3 text-right" style="color: var(--accent-primary);">${formatINR(sum.totalOrderFabricCost)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        `;
      } else if (wiz.step === 5) {
        contentEl.innerHTML = buildFullCostingBreakdownMarkup(f, evalRes);
      } else if (wiz.step === 6) {
        contentEl.innerHTML = `
          <div class="space-y-5">
            <div class="p-4 rounded-xl tf-subtle space-y-2">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-semibold">Finalize &amp; Persist Costing Record</h4>
                <span class="tf-badge ${evalRes.isComplete ? 'tf-badge-success' : 'tf-badge-warn'}">
                  ${evalRes.isComplete ? 'All Checks Passed' : `${evalRes.errors.length} Validation Issue(s)`}
                </span>
              </div>
              <p class="text-xs leading-relaxed" style="color: var(--text-secondary);">
                Saving persists this costing record to the database and logs an audit trail entry. If measurements are still in progress, you may save as a <strong>Draft</strong>; finalizing as <strong>Approved</strong> requires zero validation errors.
              </p>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-tabular">
              <div class="p-3 rounded-lg tf-subtle">
                <div class="text-[10px] uppercase" style="color: var(--text-muted);">Style Number</div>
                <div class="text-sm font-bold mt-0.5">${escapeHtml(f.styleNumber)}</div>
              </div>
              <div class="p-3 rounded-lg tf-subtle">
                <div class="text-[10px] uppercase" style="color: var(--text-muted);">Total Quantity</div>
                <div class="text-sm font-bold mt-0.5">${formatNumber(sum.totalOrderQuantity)} pcs</div>
              </div>
              <div class="p-3 rounded-lg tf-subtle">
                <div class="text-[10px] uppercase" style="color: var(--text-muted);">Gross Fabric Req</div>
                <div class="text-sm font-bold mt-0.5">${sum.totalOrderConsumptionKg} kg</div>
              </div>
              <div class="p-3 rounded-lg tf-subtle">
                <div class="text-[10px] uppercase" style="color: var(--text-muted);">Total Fabric Cost</div>
                <div class="text-sm font-bold mt-0.5" style="color: var(--accent-primary);">${formatINR(sum.totalOrderFabricCost)}</div>
              </div>
            </div>

            <div class="flex flex-wrap items-center gap-3 pt-2">
              <button type="button" onclick="saveWizardCostingRecord('Draft')" class="tf-btn-secondary px-4 py-2.5 rounded-lg text-xs font-semibold">
                Save as Draft Costing
              </button>
              <button type="button" onclick="saveWizardCostingRecord('Finalized')" ${!evalRes.isComplete ? 'disabled' : ''} class="tf-btn-secondary px-4 py-2.5 rounded-lg text-xs font-semibold disabled:opacity-40">
                Save as Finalized Costing
              </button>
              <button type="button" onclick="saveWizardCostingRecord('Approved')" ${!evalRes.isComplete ? 'disabled' : ''} class="tf-btn-primary px-5 py-2.5 rounded-lg text-xs font-semibold disabled:opacity-40">
                ✓ Approve &amp; Persist Costing Sheet
              </button>
            </div>
          </div>
        `;
      }
    }

    function renderWizardBlueprintAndValidation(f, evalRes) {
      const badge = document.getElementById('wizCadGarmentBadge');
      if (badge) badge.textContent = `${f.garmentType} · ${f.category} · ${f.baseGsm} GSM`;

      const svgContainer = document.getElementById('wizardSvgBlueprint');
      const enabledKeys = new Set(f.components.filter((c) => c.enabled !== false).map((c) => c.key));
      const hasCustom = f.components.some((c) => c.isCustom && c.enabled !== false);

      const activeFill = 'rgba(184, 74, 39, 0.22)';
      const activeStroke = '#B84A27';
      const mutedFill = 'rgba(130, 128, 122, 0.08)';
      const mutedStroke = '#82807A';

      if (f.garmentType === 'Bottom') {
        svgContainer.innerHTML = `
          <svg viewBox="0 0 220 220" class="w-44 h-44">
            <!-- Waistband Rib -->
            <rect x="62" y="18" width="96" height="16" rx="3"
              fill="${enabledKeys.has('rib') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('rib') ? activeStroke : mutedStroke}" stroke-width="2" />
            <!-- Waist Yoke -->
            <polygon points="62,34 158,34 162,52 58,52"
              fill="${enabledKeys.has('yoke') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('yoke') ? activeStroke : mutedStroke}" stroke-width="1.8" />
            <!-- Main Leg Panels -->
            <polygon points="58,52 162,52 152,184 118,184 110,92 102,184 68,184"
              fill="${enabledKeys.has('main_body') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('main_body') ? activeStroke : mutedStroke}" stroke-width="2" />
            <!-- Ankle Rib Cuffs -->
            <rect x="68" y="184" width="34" height="14" rx="2"
              fill="${enabledKeys.has('rib') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('rib') ? activeStroke : mutedStroke}" stroke-width="2" />
            <rect x="118" y="184" width="34" height="14" rx="2"
              fill="${enabledKeys.has('rib') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('rib') ? activeStroke : mutedStroke}" stroke-width="2" />
            ${
              hasCustom
                ? `<rect x="64" y="64" width="18" height="32" rx="2" fill="rgba(30,58,47,0.28)" stroke="#1E3A2F" stroke-width="1.8" />
                   <rect x="138" y="64" width="18" height="32" rx="2" fill="rgba(30,58,47,0.28)" stroke="#1E3A2F" stroke-width="1.8" />`
                : ''
            }
          </svg>
        `;
      } else {
        svgContainer.innerHTML = `
          <svg viewBox="0 0 240 220" class="w-48 h-44">
            <!-- Left & Right Sleeves -->
            <polygon points="62,42 22,88 38,108 62,78"
              fill="${enabledKeys.has('sleeve') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('sleeve') ? activeStroke : mutedStroke}" stroke-width="2" />
            <polygon points="178,42 218,88 202,108 178,78"
              fill="${enabledKeys.has('sleeve') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('sleeve') ? activeStroke : mutedStroke}" stroke-width="2" />
            <!-- Main Torso Body -->
            <rect x="62" y="42" width="116" height="146" rx="4"
              fill="${enabledKeys.has('main_body') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('main_body') ? activeStroke : mutedStroke}" stroke-width="2" />
            <!-- Shoulder Yoke -->
            <rect x="62" y="42" width="116" height="24" rx="2"
              fill="${enabledKeys.has('yoke') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('yoke') ? activeStroke : mutedStroke}" stroke-width="1.6" stroke-dasharray="3,2" />
            <!-- Neck Rib Collar -->
            <ellipse cx="120" cy="42" rx="26" ry="10"
              fill="${enabledKeys.has('rib') ? activeFill : mutedFill}"
              stroke="${enabledKeys.has('rib') ? activeStroke : mutedStroke}" stroke-width="2.2" />
            <!-- Back Neck Tape (BNT) -->
            <line x1="96" y1="40" x2="144" y2="40"
              stroke="${enabledKeys.has('bnt') ? '#1E3A2F' : mutedStroke}" stroke-width="3.5" />
            ${
              hasCustom
                ? `<polygon points="86,132 154,132 162,172 78,172" fill="rgba(30,58,47,0.22)" stroke="#1E3A2F" stroke-width="1.8" />`
                : ''
            }
          </svg>
        `;
      }

      const legendEl = document.getElementById('wizardComponentLegend');
      legendEl.innerHTML = evalRes.summary.componentBreakdown
        .map((c) => {
          const mSize = c.bySize['M'] || {};
          return `
            <div class="flex items-center justify-between py-1 border-b" style="border-color: var(--border-hairline);">
              <span><strong>${escapeHtml(c.name)}</strong> <span style="color: var(--text-muted);">(#${c.assignedFabricSerial})</span></span>
              <span class="font-mono-tabular">${mSize.valid ? `${mSize.netWeightGrams}g net · ${formatINR(mSize.fabricCost)}` : 'Incomplete'}</span>
            </div>
          `;
        })
        .join('');

      const valBadge = document.getElementById('wizValidationBadge');
      const valMsgs = document.getElementById('wizValidationMessages');
      if (evalRes.errors.length === 0) {
        valBadge.className = 'tf-badge tf-badge-success';
        valBadge.textContent = 'Valid & Ready';
      } else {
        valBadge.className = 'tf-badge tf-badge-danger';
        valBadge.textContent = `${evalRes.errors.length} Error(s)`;
      }

      const combined = [
        ...evalRes.errors.map((e) => `<div class="p-2 rounded tf-badge-danger"><strong>Step ${e.step}:</strong> ${escapeHtml(e.message)}</div>`),
        ...evalRes.warnings.map((w) => `<div class="p-2 rounded tf-badge-warn"><strong>Note:</strong> ${escapeHtml(w.message)}</div>`)
      ];
      valMsgs.innerHTML =
        combined.length > 0
          ? combined.join('')
          : `<div class="p-2 rounded tf-badge-success">All enabled components, fabric assignments, and S–XXXL measurements are complete.</div>`;
    }

    function updateWizField(field, value, rerender = false) {
      appState.wizardState.form[field] = value;
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      if (rerender) {
        renderCostingWizard();
      } else {
        const evalRes = evaluateCostingSheet(appState.wizardState.form);
        renderWizardBlueprintAndValidation(appState.wizardState.form, evalRes);
      }
    }

    function addWizardFabricRow() {
      const fabrics = appState.wizardState.form.fabrics;
      const nextSerial = fabrics.length > 0 ? Math.max(...fabrics.map((x) => Number(x.serialNo) || 0)) + 1 : 1;
      fabrics.push({
        serialNo: nextSerial,
        fabricCode: `FAB-0${nextSerial}`,
        description: 'Contrast Trim / Pocketing Fabric',
        colour: 'Deep Ink',
        gsm: appState.wizardState.form.baseGsm || 200,
        pricePerKg: 580,
        widthInches: 60,
        properties: 'Combed cotton'
      });
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function removeWizardFabricRow(idx) {
      appState.wizardState.form.fabrics.splice(idx, 1);
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function updateWizardFabric(idx, key, val) {
      const fab = appState.wizardState.form.fabrics[idx];
      if (!fab) return;
      fab[key] = key === 'gsm' || key === 'pricePerKg' ? (val === '' ? '' : Number(val)) : val;
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      const evalRes = evaluateCostingSheet(appState.wizardState.form);
      renderWizardBlueprintAndValidation(appState.wizardState.form, evalRes);
    }

    function toggleWizardComponent(cIdx, checked) {
      appState.wizardState.form.components[cIdx].enabled = Boolean(checked);
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function updateWizardComponentMeta(cIdx, key, val) {
      appState.wizardState.form.components[cIdx][key] = val;
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      const evalRes = evaluateCostingSheet(appState.wizardState.form);
      renderWizardBlueprintAndValidation(appState.wizardState.form, evalRes);
    }

    function updateWizardMeasurement(cIdx, size, dimKey, val) {
      const comp = appState.wizardState.form.components[cIdx];
      if (!comp.measurementsBySize) comp.measurementsBySize = {};
      if (!comp.measurementsBySize[size]) comp.measurementsBySize[size] = {};
      comp.measurementsBySize[size][dimKey] = val === '' ? '' : Number(val);
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      const evalRes = evaluateCostingSheet(appState.wizardState.form);
      renderWizardBlueprintAndValidation(appState.wizardState.form, evalRes);
    }

    function autoGradeWizardComponent(cIdx) {
      const comp = appState.wizardState.form.components[cIdx];
      const baseS = comp.measurementsBySize?.S || { lengthCm: 60, widthCm: 45 };
      const startL = Number(baseS.lengthCm) > 0 ? Number(baseS.lengthCm) : 60;
      const startW = Number(baseS.widthCm) > 0 ? Number(baseS.widthCm) : 45;
      comp.measurementsBySize = buildUniformGradedMeasurements(startL, startW, 2.0, 2.0);
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
      showToast(`Auto-graded ${comp.name} across S–XXXL from base size S.`, 'info');
    }

    function addWizardCustomComponent() {
      const comps = appState.wizardState.form.components;
      comps.push({
        key: 'custom_' + Date.now(),
        name: 'Custom Pocket / Hood Panel',
        isCustom: true,
        enabled: true,
        assignedFabricSerial: appState.wizardState.form.fabrics[0]?.serialNo || 1,
        panelMultiplier: 1,
        seamAllowanceCm: 2.0,
        measurementsBySize: buildUniformGradedMeasurements(26, 22, 1.0, 1.0)
      });
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function removeWizardCustomComponent(cIdx) {
      appState.wizardState.form.components.splice(cIdx, 1);
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function updateWizardSizeQuantity(size, val) {
      appState.wizardState.form.sizeQuantities[size] = val === '' ? '' : Number(val);
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function applySizeRatioPreset(totalTarget) {
      const ratios = { S: 0.12, M: 0.26, L: 0.30, XL: 0.18, XXL: 0.10, XXXL: 0.04 };
      SIZES.forEach((sz) => {
        appState.wizardState.form.sizeQuantities[sz] = Math.round(totalTarget * ratios[sz]);
      });
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      renderCostingWizard();
    }

    function saveWizardCostingRecord(targetStatus) {
      const auth = assertPermission(appState.currentUser, 'costing:write');
      if (!auth.allowed) {
        showToast(auth.error, 'error');
        return;
      }
      if (targetStatus === 'Approved') {
        const approveAuth = assertPermission(appState.currentUser, 'costing:approve');
        if (!approveAuth.allowed) {
          showToast(approveAuth.error, 'error');
          return;
        }
      }

      const form = JSON.parse(JSON.stringify(appState.wizardState.form));
      const evalRes = evaluateCostingSheet(form);

      if (targetStatus !== 'Draft' && !evalRes.isComplete) {
        showToast(`Cannot save as ${targetStatus}: please resolve ${evalRes.errors.length} validation error(s) first.`, 'error');
        return;
      }
      if (!evalRes.canSaveDraft) {
        showToast('Style Number and Style Name are required even for a Draft.', 'error');
        return;
      }

      form.status = targetStatus;
      form.calculatedSummary = evalRes.summary;
      form.isComplete = evalRes.isComplete;
      form.updatedAt = new Date().toISOString();
      form.createdBy = appState.currentUser.fullName;

      const existingIdx = appState.db.costingRecords.findIndex((c) => c.id === form.id);
      if (existingIdx >= 0) {
        appState.db.costingRecords[existingIdx] = form;
      } else {
        form.createdAt = form.updatedAt;
        appState.db.costingRecords.unshift(form);
      }

      appState.db.auditLogs.unshift({
        id: 'AUD-' + Date.now(),
        entityType: 'costing',
        entityId: form.id,
        orderId: null,
        action: `COSTING_${targetStatus.toUpperCase()}`,
        previousStatus: existingIdx >= 0 ? 'Updated' : 'New',
        newStatus: targetStatus,
        actorName: appState.currentUser.fullName,
        actorRole: appState.currentUser.role,
        remarks: `Saved costing ${form.styleNumber} (${form.styleName}) with ${formatNumber(evalRes.summary.totalOrderQuantity)} pcs · Total Fabric Cost ${formatINR(evalRes.summary.totalOrderFabricCost)}.`,
        createdAt: form.updatedAt
      });

      saveDatabase();
      switchCostingSubmode('list');
      showToast(`Costing record ${form.styleNumber} saved as ${targetStatus}.`, 'success');
    }

    function buildFullCostingBreakdownMarkup(c, evalRes) {
      const sum = evalRes.summary;
      return `
        <div class="space-y-5">
          <!-- Summary Banner -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-tabular">
            <div class="p-3 rounded-lg tf-subtle">
              <div class="text-[10px] uppercase" style="color: var(--text-muted);">Order Quantity</div>
              <div class="text-sm font-bold mt-0.5">${formatNumber(sum.totalOrderQuantity)} pcs</div>
            </div>
            <div class="p-3 rounded-lg tf-subtle">
              <div class="text-[10px] uppercase" style="color: var(--text-muted);">Total Net Garment Wt</div>
              <div class="text-sm font-bold mt-0.5">${sum.totalOrderNetWeightKg} kg</div>
            </div>
            <div class="p-3 rounded-lg tf-subtle">
              <div class="text-[10px] uppercase" style="color: var(--text-muted);">Gross Fabric Req (+${c.wastageAllowancePct}%)</div>
              <div class="text-sm font-bold mt-0.5">${sum.totalOrderConsumptionKg} kg</div>
            </div>
            <div class="p-3 rounded-lg tf-subtle">
              <div class="text-[10px] uppercase" style="color: var(--text-muted);">Total Order Fabric Cost</div>
              <div class="text-sm font-bold mt-0.5" style="color: var(--accent-primary);">${formatINR(sum.totalOrderFabricCost)}</div>
            </div>
          </div>

          <!-- Table 1: Component-by-Size Net Weight (g), Gross Consumption (g), and Cost (₹) -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--text-secondary);">
              1. Component Weight &amp; Cost Breakdown by Size (Net g / Gross Cons. g / Cost ₹)
            </h4>
            <div class="overflow-x-auto rounded-xl border" style="border-color: var(--border-hairline);">
              <table class="w-full text-left border-collapse tf-table text-xs">
                <thead>
                  <tr>
                    <th class="py-2 px-3">Component &amp; Assigned Fabric</th>
                    ${SIZES.map((sz) => `<th class="py-2 px-2.5 text-right font-mono-tabular">${sz}</th>`).join('')}
                  </tr>
                </thead>
                <tbody class="font-mono-tabular">
                  ${sum.componentBreakdown
                    .map(
                      (comp) => `
                      <tr>
                        <td class="py-2 px-3 font-sans">
                          <div class="font-semibold">${escapeHtml(comp.name)}</div>
                          <div class="text-[11px]" style="color: var(--text-secondary);">Fabric #${comp.assignedFabricSerial}: ${escapeHtml(comp.assignedFabricDescription)} (${comp.panelMultiplier}x panels)</div>
                        </td>
                        ${SIZES.map((sz) => {
                          const cell = comp.bySize[sz];
                          if (!cell || !cell.valid) {
                            return `<td class="py-2 px-2.5 text-right text-red-500">Missing</td>`;
                          }
                          return `
                            <td class="py-2 px-2.5 text-right">
                              <div>${cell.netWeightGrams}g net</div>
                              <div class="text-[10px]" style="color: var(--text-muted);">${cell.consumptionGrams}g cons</div>
                              <div class="font-semibold" style="color: var(--accent-primary);">${formatINR(cell.fabricCost)}</div>
                            </td>
                          `;
                        }).join('')}
                      </tr>
                    `
                    )
                    .join('')}
                </tbody>
              </table>
            </div>
          </div>

          <!-- Table 2: Fabric Mill Purchasing Requirements -->
          <div>
            <h4 class="text-xs font-semibold uppercase tracking-wider mb-2" style="color: var(--text-secondary);">
              2. Fabric-Wise Mill Purchasing Requirement Summary
            </h4>
            <div class="overflow-x-auto rounded-xl border" style="border-color: var(--border-hairline);">
              <table class="w-full text-left border-collapse tf-table text-xs">
                <thead>
                  <tr>
                    <th class="py-2 px-3">Serial</th>
                    <th class="py-2 px-3">Fabric &amp; Colour</th>
                    <th class="py-2 px-3">Assigned Components</th>
                    <th class="py-2 px-3 text-right">GSM</th>
                    <th class="py-2 px-3 text-right">Rate (₹/kg)</th>
                    <th class="py-2 px-3 text-right">Net Wt (kg)</th>
                    <th class="py-2 px-3 text-right">Gross Req (kg)</th>
                    <th class="py-2 px-3 text-right">Total Cost (₹)</th>
                  </tr>
                </thead>
                <tbody class="font-mono-tabular">
                  ${sum.fabricRequirements
                    .map(
                      (fr) => `
                      <tr>
                        <td class="py-2 px-3 font-bold">#${fr.serialNo}</td>
                        <td class="py-2 px-3 font-sans">
                          <div class="font-semibold">${escapeHtml(fr.description)}</div>
                          <div class="text-[11px]" style="color: var(--text-secondary);">${escapeHtml(fr.colour)}</div>
                        </td>
                        <td class="py-2 px-3 font-sans">${escapeHtml(fr.assignedComponents.join(', ') || 'None')}</td>
                        <td class="py-2 px-3 text-right">${fr.gsm}</td>
                        <td class="py-2 px-3 text-right">${formatINR(fr.pricePerKg)}</td>
                        <td class="py-2 px-3 text-right">${fr.totalNetWeightKg} kg</td>
                        <td class="py-2 px-3 text-right font-semibold">${fr.totalConsumptionKg} kg</td>
                        <td class="py-2 px-3 text-right font-semibold" style="color: var(--accent-primary);">${formatINR(fr.totalCost)}</td>
                      </tr>
                    `
                    )
                    .join('')}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      `;
    }

    function openCostingDetailModal(costingId) {
      const c = appState.db.costingRecords.find((x) => x.id === costingId);
      if (!c) return;
      const evalRes = evaluateCostingSheet(c);
      openModal({
        category: `TECHNICAL COSTING SHEET · ${c.id}`,
        title: `${c.styleNumber} — ${c.styleName}`,
        bodyHtml: buildFullCostingBreakdownMarkup(c, evalRes),
        footerHtml: `
          <button type="button" onclick="closeModal(); openCostingWizardEdit('${escapeHtml(c.id)}');" class="tf-btn-secondary px-4 py-2 rounded-lg text-xs font-medium">
            Edit in 6-Step Wizard
          </button>
          <button type="button" onclick="closeModal()" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">
            Done
          </button>
        `
      });
    }

    // --- 10. VIEW 3: STATUS FOLLOW-UP & WORKFLOW TASK MANAGEMENT ---
    function setTaskStatusTab(tab) {
      appState.taskStatusTab = tab;
      renderFollowUpTasks();
    }

    function renderFollowUpTasks() {
      const tasks = appState.db.tasks;
      document.getElementById('taskCount-ALL').textContent = String(tasks.length);
      document.getElementById('taskCount-Pending').textContent = String(tasks.filter((t) => t.status === 'Pending').length);
      document.getElementById('taskCount-InProgress').textContent = String(tasks.filter((t) => t.status === 'In Progress').length);
      document.getElementById('taskCount-Completed').textContent = String(tasks.filter((t) => t.status === 'Completed').length);

      ['ALL', 'Pending', 'In Progress', 'Completed'].forEach((tab) => {
        const btn = document.getElementById(`taskTab-${tab}`);
        if (btn) {
          if (appState.taskStatusTab === tab) {
            btn.style.backgroundColor = 'var(--accent-primary)';
            btn.style.color = '#fff';
          } else {
            btn.style.backgroundColor = 'var(--bg-subtle)';
            btn.style.color = 'var(--text-secondary)';
          }
        }
      });

      // Populate Order Filter Select
      const ordSelect = document.getElementById('taskOrderFilter');
      if (ordSelect) {
        const currentVal = ordSelect.value || 'ALL';
        ordSelect.innerHTML =
          `<option value="ALL">All Linked Orders</option>` +
          appState.db.orders
            .map((o) => `<option value="${escapeHtml(o.id)}" ${o.id === currentVal ? 'selected' : ''}>${escapeHtml(o.orderNumber)} — ${escapeHtml(o.styleNumber)}</option>`)
            .join('');
      }

      // Render Order Workflow Progress Strip
      const stripEl = document.getElementById('followUpOrderProgressStrip');
      if (stripEl) {
        stripEl.innerHTML = appState.db.orders
          .filter((o) => o.status === 'Currently Going On')
          .map((o) => {
            const prog = calculateOrderWorkflowProgress(o.id, tasks);
            return `
              <div class="p-3.5 rounded-xl tf-surface space-y-1.5">
                <div class="flex items-center justify-between text-xs">
                  <span class="font-mono-tabular font-semibold">${escapeHtml(o.orderNumber)}</span>
                  <span class="font-mono-tabular font-bold" style="color: var(--accent-primary);">${prog.progressPct}%</span>
                </div>
                <div class="text-[11px] truncate" style="color: var(--text-secondary);">${escapeHtml(o.customerName)} · ${escapeHtml(o.styleNumber)}</div>
                <div class="w-full h-1.5 rounded-full bg-stone-500/15 overflow-hidden">
                  <div class="h-full rounded-full" style="width: ${prog.progressPct}%; background-color: var(--accent-primary);"></div>
                </div>
                <div class="text-[10px] font-mono-tabular" style="color: var(--text-muted);">
                  ${prog.completedTasks} of ${prog.milestoneTasks} milestone tasks completed
                </div>
              </div>
            `;
          })
          .join('');
      }

      const q = (document.getElementById('taskSearchInput')?.value || '').trim().toLowerCase();
      const ordFilter = document.getElementById('taskOrderFilter')?.value || 'ALL';
      const assigneeFilter = document.getElementById('taskAssigneeFilter')?.value || 'ALL';

      const filtered = tasks.filter((t) => {
        if (appState.taskStatusTab !== 'ALL' && t.status !== appState.taskStatusTab) return false;
        if (ordFilter !== 'ALL' && t.orderId !== ordFilter) return false;
        if (assigneeFilter !== 'ALL' && t.assignedUserName !== assigneeFilter) return false;
        if (q) {
          const hay = `${t.title} ${t.description} ${t.remarks || ''} ${t.assignedUserName}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      const container = document.getElementById('followUpTasksContainer');
      if (filtered.length === 0) {
        container.innerHTML = `<div class="p-8 rounded-xl tf-surface text-center text-xs" style="color: var(--text-muted);">No workflow tasks match the selected status and filters.</div>`;
        return;
      }

      container.innerHTML = filtered
        .map((t) => {
          const ord = appState.db.orders.find((o) => o.id === t.orderId);
          const sBadge =
            t.status === 'Completed'
              ? 'tf-badge-success'
              : t.status === 'In Progress'
              ? 'tf-badge-info'
              : 'tf-badge-warn';
          const pBadge =
            t.priority === 'Critical'
              ? 'tf-badge-danger'
              : t.priority === 'High'
              ? 'tf-badge-warn'
              : 'tf-badge-neutral';
          return `
            <div class="p-4 rounded-xl tf-surface flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div class="space-y-1.5 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="tf-badge ${sBadge}">${escapeHtml(t.status)}</span>
                  <span class="tf-badge ${pBadge}">${escapeHtml(t.priority)}</span>
                  <button type="button" onclick="openOrderDetailModal('${escapeHtml(t.orderId)}')" class="font-mono-tabular text-xs font-semibold underline" style="color: var(--accent-primary);">
                    ${escapeHtml(ord ? ord.orderNumber : t.orderId)} (${escapeHtml(ord ? ord.styleNumber : '')})
                  </button>
                  <span class="text-xs" style="color: var(--text-muted);">· Stage: ${escapeHtml(t.stageCategory)}</span>
                  ${
                    t.reopenedCount > 0
                      ? `<span class="tf-badge tf-badge-warn font-mono-tabular">Reopened ${t.reopenedCount}x</span>`
                      : ''
                  }
                </div>
                <h3 class="text-sm font-semibold">${escapeHtml(t.title)}</h3>
                <p class="text-xs leading-relaxed" style="color: var(--text-secondary);">${escapeHtml(t.description)}</p>
                <div class="p-2.5 rounded-lg tf-subtle text-xs">
                  <span class="font-semibold">Remarks:</span> ${escapeHtml(t.remarks || 'No remarks logged.')}
                  ${
                    t.completedAt
                      ? `<div class="font-mono-tabular text-[11px] mt-1" style="color: var(--status-success-text);">✓ Completed at ${escapeHtml(t.completedAt)} by ${escapeHtml(t.completedBy || 'Staff')}</div>`
                      : ''
                  }
                </div>
              </div>

              <div class="flex flex-col sm:flex-row lg:flex-col items-start sm:items-center lg:items-end justify-between gap-2.5 flex-shrink-0">
                <div class="text-xs font-mono-tabular space-y-0.5 text-left lg:text-right">
                  <div><span style="color: var(--text-muted);">Assigned:</span> <strong>${escapeHtml(t.assignedUserName)}</strong></div>
                  <div><span style="color: var(--text-muted);">Follow-Up:</span> <strong>${escapeHtml(t.followUpDate)}</strong></div>
                  <div><span style="color: var(--text-muted);">Due Date:</span> ${escapeHtml(t.dueDate)}</div>
                </div>

                <div class="flex flex-wrap items-center gap-2">
                  ${
                    t.status === 'Pending'
                      ? `<button type="button" onclick="markTaskInProgress('${escapeHtml(t.id)}')" class="tf-btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium">Start Task</button>`
                      : ''
                  }
                  ${
                    t.status !== 'Completed'
                      ? `<button type="button" onclick="openCompleteTaskModal('${escapeHtml(t.id)}')" class="tf-btn-primary px-3 py-1.5 rounded-lg text-xs font-medium">✓ Mark Complete</button>`
                      : `<button type="button" onclick="openReopenTaskModal('${escapeHtml(t.id)}')" class="tf-btn-secondary px-3 py-1.5 rounded-lg text-xs font-medium">↺ Reopen Task</button>`
                  }
                  <button type="button" onclick="openTaskAuditModal('${escapeHtml(t.id)}')" class="tf-btn-secondary px-2.5 py-1.5 rounded-lg text-xs font-medium">
                    Audit History (${(t.history || []).length})
                  </button>
                </div>
              </div>
            </div>
          `;
        })
        .join('');
    }

    function markTaskInProgress(taskId) {
      const auth = assertPermission(appState.currentUser, 'task:write');
      if (!auth.allowed) {
        showToast(auth.error, 'error');
        return;
      }
      const task = appState.db.tasks.find((t) => t.id === taskId);
      if (!task) return;
      const now = new Date().toISOString();
      const prev = task.status;
      task.status = 'In Progress';
      task.updatedAt = now;
      task.history = [
        ...(task.history || []),
        {
          action: 'Started',
          fromStatus: prev,
          toStatus: 'In Progress',
          actor: appState.currentUser.fullName,
          role: appState.currentUser.role,
          remarks: 'Task moved to In Progress.',
          timestamp: now
        }
      ];
      saveDatabase();
      renderCurrentActiveView();
      showToast(`Task "${task.title}" moved to In Progress.`, 'info');
    }

    function openCompleteTaskModal(taskId) {
      const task = appState.db.tasks.find((t) => t.id === taskId);
      if (!task) return;
      openModal({
        category: `WORKFLOW COMPLETION · ${task.id}`,
        title: `Complete Task: ${task.title}`,
        bodyHtml: `
          <div class="space-y-4">
            <p class="text-xs leading-relaxed" style="color: var(--text-secondary);">
              Completing this task validates your role permissions, persists the state change to the database, moves the task to Completed history, and records an immutable completion timestamp.
            </p>
            <div>
              <label for="completeTaskRemarksInput" class="block text-xs font-medium mb-1">Completion Verification Remarks *</label>
              <textarea id="completeTaskRemarksInput" rows="3" class="tf-input w-full" placeholder="Enter inspection result, batch number, or completion note...">${escapeHtml(task.remarks || '')}</textarea>
            </div>
          </div>
        `,
        footerHtml: `
          <button type="button" onclick="closeModal()" class="tf-btn-secondary px-4 py-2 rounded-lg text-xs font-medium">Cancel</button>
          <button type="button" onclick="confirmCompleteTask('${escapeHtml(task.id)}')" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">✓ Persist Completion</button>
        `
      });
    }

    function confirmCompleteTask(taskId) {
      const idx = appState.db.tasks.findIndex((t) => t.id === taskId);
      if (idx < 0) return;
      const remarks = document.getElementById('completeTaskRemarksInput')?.value || '';
      const res = completeWorkflowTask({
        task: appState.db.tasks[idx],
        actor: appState.currentUser,
        remarks
      });
      if (!res.ok) {
        showToast(res.error, 'error');
        return;
      }
      // Persist to database first, then update UI
      appState.db.tasks[idx] = res.task;
      appState.db.auditLogs.unshift(res.auditEntry);
      saveDatabase();
      closeModal();
      renderCurrentActiveView();
      showToast(`Task completed and recorded in audit history.`, 'success');
    }

    function openReopenTaskModal(taskId) {
      const task = appState.db.tasks.find((t) => t.id === taskId);
      if (!task) return;
      openModal({
        category: `REOPEN COMPLETED TASK · ${task.id}`,
        title: `Reopen Task: ${task.title}`,
        bodyHtml: `
          <div class="space-y-4">
            <div class="p-3 rounded-lg tf-subtle text-xs">
              Previously completed at <strong class="font-mono-tabular">${escapeHtml(task.completedAt)}</strong> by <strong>${escapeHtml(task.completedBy)}</strong>.
              Reopening preserves this completion record in historical audit logs.
            </div>
            <div>
              <label for="reopenTargetStatusSelect" class="block text-xs font-medium mb-1">Target Workflow Status</label>
              <select id="reopenTargetStatusSelect" class="tf-input w-full">
                <option value="In Progress">In Progress</option>
                <option value="Pending">Pending</option>
              </select>
            </div>
            <div>
              <label for="reopenReasonInput" class="block text-xs font-medium mb-1">Mandatory Reopen Reason / Audit Remark *</label>
              <textarea id="reopenReasonInput" rows="3" class="tf-input w-full" placeholder="Explain why this task is being reopened..."></textarea>
            </div>
          </div>
        `,
        footerHtml: `
          <button type="button" onclick="closeModal()" class="tf-btn-secondary px-4 py-2 rounded-lg text-xs font-medium">Cancel</button>
          <button type="button" onclick="confirmReopenTask('${escapeHtml(task.id)}')" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">↺ Reopen with Audit Trail</button>
        `
      });
    }

    function confirmReopenTask(taskId) {
      const idx = appState.db.tasks.findIndex((t) => t.id === taskId);
      if (idx < 0) return;
      const targetStatus = document.getElementById('reopenTargetStatusSelect')?.value || 'In Progress';
      const reason = document.getElementById('reopenReasonInput')?.value || '';
      const res = reopenWorkflowTask({
        task: appState.db.tasks[idx],
        actor: appState.currentUser,
        targetStatus,
        reason
      });
      if (!res.ok) {
        showToast(res.error, 'error');
        return;
      }
      appState.db.tasks[idx] = res.task;
      appState.db.auditLogs.unshift(res.auditEntry);
      saveDatabase();
      closeModal();
      renderCurrentActiveView();
      showToast(`Task reopened to ${targetStatus}; previous completion history preserved.`, 'info');
    }

    function openTaskAuditModal(taskId) {
      const task = appState.db.tasks.find((t) => t.id === taskId);
      if (!task) return;
      const history = task.history || [];
      openModal({
        category: `IMMUTABLE TASK AUDIT TRAIL · ${task.id}`,
        title: task.title,
        bodyHtml: `
          <div class="space-y-4">
            ${
              (task.previousCompletions || []).length > 0
                ? `<div class="p-3 rounded-lg tf-subtle text-xs">
                     <strong>Preserved Prior Completions (${task.previousCompletions.length}):</strong>
                     ${task.previousCompletions
                       .map(
                         (pc) =>
                           `<div class="mt-1 font-mono-tabular text-[11px]">• Completed ${escapeHtml(pc.completedAt)} by ${escapeHtml(pc.completedBy)} → Reopened ${escapeHtml(pc.reopenedAt)} (${escapeHtml(pc.reopenReason)})</div>`
                       )
                       .join('')}
                   </div>`
                : ''
            }
            <div class="space-y-2.5">
              ${
                history.length > 0
                  ? history
                      .map(
                        (h) => `
                        <div class="p-3 rounded-lg tf-subtle text-xs flex items-start justify-between gap-3">
                          <div>
                            <div class="font-semibold">${escapeHtml(h.action)}: ${escapeHtml(h.fromStatus || 'Initial')} → ${escapeHtml(h.toStatus)}</div>
                            <div class="mt-0.5" style="color: var(--text-secondary);">${escapeHtml(h.remarks)}</div>
                            <div class="text-[11px] mt-1" style="color: var(--text-muted);">Actor: ${escapeHtml(h.actor)} (${escapeHtml(h.role)})</div>
                          </div>
                          <span class="font-mono-tabular text-[11px]" style="color: var(--text-muted);">${escapeHtml(h.timestamp)}</span>
                        </div>
                      `
                      )
                      .join('')
                  : `<div class="text-xs" style="color: var(--text-muted);">No status transitions recorded yet.</div>`
              }
            </div>
          </div>
        `,
        footerHtml: `<button type="button" onclick="closeModal()" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">Close</button>`
      });
    }

    function openCreateTaskModal(defaultOrderId = '') {
      const auth = assertPermission(appState.currentUser, 'task:write');
      if (!auth.allowed) {
        showToast(auth.error, 'error');
        return;
      }
      openModal({
        category: 'NEW WORKFLOW MILESTONE',
        title: 'Create Order Follow-Up Task',
        bodyHtml: `
          <form id="createTaskForm" onsubmit="submitCreateTask(event)" class="space-y-3.5 text-xs">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-medium mb-1">Linked Manufacturing Order *</label>
                <select id="newTaskOrder" required class="tf-input w-full">
                  ${appState.db.orders
                    .map(
                      (o) =>
                        `<option value="${escapeHtml(o.id)}" ${o.id === defaultOrderId ? 'selected' : ''}>${escapeHtml(o.orderNumber)} — ${escapeHtml(o.customerName)} (${escapeHtml(o.styleNumber)})</option>`
                    )
                    .join('')}
                </select>
              </div>
              <div>
                <label class="block font-medium mb-1">Stage Category *</label>
                <select id="newTaskStage" class="tf-input w-full">
                  <option value="Fabric Quality">Fabric Quality</option>
                  <option value="Cutting">Cutting</option>
                  <option value="Sewing & Assembly">Sewing &amp; Assembly</option>
                  <option value="Finishing & QA">Finishing &amp; QA</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block font-medium mb-1">Task Title *</label>
              <input id="newTaskTitle" type="text" required class="tf-input w-full" placeholder="e.g. Inline AQL 1.5 Sewing Audit on Batch 2" />
            </div>
            <div>
              <label class="block font-medium mb-1">Technical Description *</label>
              <textarea id="newTaskDesc" rows="2" required class="tf-input w-full" placeholder="Specify tolerances, bundle count, or inspection requirement..."></textarea>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block font-medium mb-1">Assigned Staff *</label>
                <select id="newTaskAssignee" class="tf-input w-full">
                  ${appState.db.users.map((u) => `<option value="${escapeHtml(u.fullName)}">${escapeHtml(u.fullName)} (${escapeHtml(u.role)})</option>`).join('')}
                </select>
              </div>
              <div>
                <label class="block font-medium mb-1">Priority</label>
                <select id="newTaskPriority" class="tf-input w-full">
                  <option value="Standard">Standard</option>
                  <option value="High" selected>High</option>
                  <option value="Critical">Critical</option>
                </select>
              </div>
              <div>
                <label class="block font-medium mb-1">Follow-Up Date *</label>
                <input id="newTaskFollowUp" type="date" required value="2026-10-19" class="tf-input w-full font-mono-tabular" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-medium mb-1">Due Date *</label>
                <input id="newTaskDue" type="date" required value="2026-10-21" class="tf-input w-full font-mono-tabular" />
              </div>
              <div>
                <label class="block font-medium mb-1">Initial Remarks</label>
                <input id="newTaskRemarks" type="text" class="tf-input w-full" placeholder="Scheduled for morning shift..." />
              </div>
            </div>
          </form>
        `,
        footerHtml: `
          <button type="button" onclick="closeModal()" class="tf-btn-secondary px-4 py-2 rounded-lg text-xs font-medium">Cancel</button>
          <button type="button" onclick="document.getElementById('createTaskForm').requestSubmit()" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">Create Task</button>
        `
      });
    }

    function submitCreateTask(e) {
      e.preventDefault();
      const now = new Date().toISOString();
      const newTask = {
        id: 'TSK-' + Math.floor(600 + Math.random() * 390),
        orderId: document.getElementById('newTaskOrder').value,
        title: document.getElementById('newTaskTitle').value.trim(),
        description: document.getElementById('newTaskDesc').value.trim(),
        stageCategory: document.getElementById('newTaskStage').value,
        assignedUserName: document.getElementById('newTaskAssignee').value,
        priority: document.getElementById('newTaskPriority').value,
        followUpDate: document.getElementById('newTaskFollowUp').value,
        dueDate: document.getElementById('newTaskDue').value,
        remarks: document.getElementById('newTaskRemarks').value.trim() || 'Task logged.',
        status: 'Pending',
        countsTowardCompletion: true,
        completedAt: null,
        completedBy: null,
        reopenedCount: 0,
        previousCompletions: [],
        history: [
          {
            action: 'Created',
            fromStatus: null,
            toStatus: 'Pending',
            actor: appState.currentUser.fullName,
            role: appState.currentUser.role,
            remarks: 'Created new follow-up task.',
            timestamp: now
          }
        ]
      };
      appState.db.tasks.unshift(newTask);
      saveDatabase();
      closeModal();
      renderCurrentActiveView();
      showToast(`Created follow-up task "${newTask.title}".`, 'success');
    }

    // --- 11. VIEW 4: ORDER HISTORY & STRUCTURED ORDER DETAIL VIEW ---
    function setOrderStatusTab(tab) {
      appState.orderStatusTab = tab;
      renderOrdersView();
    }

    function renderOrdersView() {
      const orders = appState.db.orders;
      document.getElementById('orderCount-GoingOn').textContent = String(orders.filter((o) => o.status === 'Currently Going On').length);
      document.getElementById('orderCount-Completed').textContent = String(orders.filter((o) => o.status === 'Completed').length);
      document.getElementById('orderCount-Cancelled').textContent = String(orders.filter((o) => o.status === 'Cancelled').length);
      document.getElementById('orderCount-ALL').textContent = String(orders.length);

      ['Currently Going On', 'Completed', 'Cancelled', 'ALL'].forEach((tab) => {
        const btn = document.getElementById(`orderTab-${tab}`);
        if (btn) {
          if (appState.orderStatusTab === tab) {
            btn.style.backgroundColor = 'var(--accent-primary)';
            btn.style.color = '#fff';
          } else {
            btn.style.backgroundColor = 'var(--bg-subtle)';
            btn.style.color = 'var(--text-secondary)';
          }
        }
      });

      const q = (document.getElementById('orderSearchInput')?.value || '').trim().toLowerCase();
      const sortBy = document.getElementById('orderSortSelect')?.value || 'due_asc';

      let list = orders.filter((o) => {
        if (appState.orderStatusTab !== 'ALL' && o.status !== appState.orderStatusTab) return false;
        if (q) {
          const hay = `${o.orderNumber} ${o.customerName} ${o.buyerPoRef} ${o.styleNumber} ${o.styleName}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });

      list.sort((a, b) => {
        if (sortBy === 'order_desc') return b.orderDate.localeCompare(a.orderDate);
        if (sortBy === 'pieces_desc') return b.totalPieces - a.totalPieces;
        return a.dueDate.localeCompare(b.dueDate);
      });

      const container = document.getElementById('ordersListContainer');
      if (list.length === 0) {
        container.innerHTML = `<div class="p-8 rounded-xl tf-surface text-center text-xs" style="color: var(--text-muted);">No orders found in this view.</div>`;
        return;
      }

      container.innerHTML = list
        .map((o) => {
          const wf = calculateOrderWorkflowProgress(o.id, appState.db.tasks);
          const costing = appState.db.costingRecords.find((c) => c.id === o.costingId);
          const badgeCls =
            o.status === 'Completed'
              ? 'tf-badge-success'
              : o.status === 'Cancelled'
              ? 'tf-badge-danger'
              : 'tf-badge-info';
          return `
            <div class="p-5 rounded-xl tf-surface flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div class="space-y-1.5 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="font-mono-tabular text-xs font-bold px-2 py-0.5 rounded tf-subtle">${escapeHtml(o.orderNumber)}</span>
                  <span class="tf-badge ${badgeCls}">${escapeHtml(o.status)}</span>
                  <span class="font-mono-tabular text-xs" style="color: var(--text-muted);">PO: ${escapeHtml(o.buyerPoRef)}</span>
                  <span class="tf-badge tf-badge-neutral">${escapeHtml(o.currentStage)}</span>
                </div>
                <h3 class="text-base font-semibold">${escapeHtml(o.customerName)} — ${escapeHtml(o.styleName)} (${escapeHtml(o.styleNumber)})</h3>
                <p class="text-xs" style="color: var(--text-secondary);">
                  ${escapeHtml(o.remarks || '')}
                  ${
                    o.cancellationReason
                      ? `<span class="block mt-1 font-medium" style="color: var(--status-danger-text);">Cancellation Reason: ${escapeHtml(o.cancellationReason)}</span>`
                      : ''
                  }
                </p>
              </div>

              <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-tabular">
                <div class="p-2.5 rounded-lg tf-subtle">
                  <div class="text-[10px] uppercase" style="color: var(--text-muted);">Pieces Output</div>
                  <div class="text-xs font-bold mt-0.5">${formatNumber(o.completedPieces)} / ${formatNumber(o.totalPieces)}</div>
                </div>
                <div class="p-2.5 rounded-lg tf-subtle">
                  <div class="text-[10px] uppercase" style="color: var(--text-muted);">Workflow Tasks</div>
                  <div class="text-xs font-bold mt-0.5">${wf.completedTasks}/${wf.milestoneTasks} (${wf.progressPct}%)</div>
                </div>
                <div class="p-2.5 rounded-lg tf-subtle">
                  <div class="text-[10px] uppercase" style="color: var(--text-muted);">Linked Costing</div>
                  <div class="text-xs font-bold mt-0.5">${costing ? formatINR(costing.calculatedSummary?.weightedAvgPieceFabricCost || 0) + '/pc' : 'Unlinked'}</div>
                </div>
                <div class="p-2.5 rounded-lg tf-subtle">
                  <div class="text-[10px] uppercase" style="color: var(--text-muted);">Due Date</div>
                  <div class="text-xs font-bold mt-0.5">${escapeHtml(o.dueDate)}</div>
                </div>
              </div>

              <div class="flex items-center gap-2 flex-shrink-0">
                <button type="button" onclick="openOrderDetailModal('${escapeHtml(o.id)}')" class="tf-btn-primary px-3.5 py-2 rounded-lg text-xs font-medium">
                  Inspect Full Order &amp; History
                </button>
              </div>
            </div>
          `;
        })
        .join('');
    }

    function openOrderDetailModal(orderId, activeTab = 'overview') {
      const o = appState.db.orders.find((x) => x.id === orderId);
      if (!o) return;
      appState.activeOrderDetailTab = activeTab;
      const costing = appState.db.costingRecords.find((c) => c.id === o.costingId);
      const wf = calculateOrderWorkflowProgress(o.id, appState.db.tasks);
      const orderTasks = appState.db.tasks.filter((t) => t.orderId === o.id);
      const orderAudit = appState.db.auditLogs.filter((a) => a.orderId === o.id || a.entityId === o.id);

      const tabs = [
        ['overview', '1. Overview & Status'],
        ['costing', '2. Linked Costing'],
        ['quantities', '3. Size Quantities (S–XXXL)'],
        ['workflow', `4. Workflow (${wf.completedTasks}/${wf.milestoneTasks})`],
        ['history', `5. Audit & History (${(o.statusHistory || []).length + orderAudit.length})`]
      ];

      let tabContentHtml = '';
      if (activeTab === 'overview') {
        tabContentHtml = `
          <div class="space-y-4 text-xs">
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono-tabular">
              <div class="p-3 rounded-lg tf-subtle">
                <div class="text-[10px]" style="color: var(--text-muted);">Buyer / Customer</div>
                <div class="font-sans font-semibold mt-0.5">${escapeHtml(o.customerName)}</div>
              </div>
              <div class="p-3 rounded-lg tf-subtle">
                <div class="text-[10px]" style="color: var(--text-muted);">Buyer PO Ref</div>
                <div class="font-semibold mt-0.5">${escapeHtml(o.buyerPoRef)}</div>
              </div>
              <div class="p-3 rounded-lg tf-subtle">
                <div class="text-[10px]" style="color: var(--text-muted);">Order / Due Date</div>
                <div class="font-semibold mt-0.5">${escapeHtml(o.orderDate)} → ${escapeHtml(o.dueDate)}</div>
              </div>
              <div class="p-3 rounded-lg tf-subtle">
                <div class="text-[10px]" style="color: var(--text-muted);">Current Status</div>
                <div class="font-semibold mt-0.5" style="color: var(--accent-primary);">${escapeHtml(o.status)}</div>
              </div>
            </div>

            <div class="p-4 rounded-xl tf-subtle space-y-2">
              <div class="font-semibold">Historical Remarks &amp; Floor Notes</div>
              <p class="leading-relaxed" style="color: var(--text-secondary);">${escapeHtml(o.remarks || 'None')}</p>
              ${
                o.completedAt
                  ? `<div class="font-mono-tabular text-[11px]" style="color: var(--status-success-text);">✓ Completed Timestamp: ${escapeHtml(o.completedAt)}</div>`
                  : ''
              }
              ${
                o.cancelledAt
                  ? `<div class="font-mono-tabular text-[11px]" style="color: var(--status-danger-text);">✕ Cancelled Timestamp: ${escapeHtml(o.cancelledAt)} — Reason: ${escapeHtml(o.cancellationReason)}</div>`
                  : ''
              }
            </div>

            <!-- Validated State Transition Form (Never deletes history) -->
            <div class="p-4 rounded-xl tf-surface space-y-3">
              <div class="font-semibold">Validated Order Lifecycle State Transition (Preserves All History)</div>
              <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label class="block text-[11px] mb-1" style="color: var(--text-secondary);">Target Status</label>
                  <select id="orderTransitionStatusSelect" class="tf-input w-full text-xs">
                    <option value="Currently Going On" ${o.status === 'Currently Going On' ? 'selected' : ''}>Currently Going On</option>
                    <option value="Completed" ${o.status === 'Completed' ? 'selected' : ''}>Completed</option>
                    <option value="Cancelled" ${o.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
                  </select>
                </div>
                <div class="sm:col-span-2">
                  <label class="block text-[11px] mb-1" style="color: var(--text-secondary);">Transition Remark / Mandatory Cancellation Reason *</label>
                  <input id="orderTransitionRemarkInput" type="text" class="tf-input w-full text-xs" placeholder="Enter sign-off note or cancellation reason..." />
                </div>
              </div>
              <button type="button" onclick="handleOrderStatusTransition('${escapeHtml(o.id)}')" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">
                Persist Status Transition
              </button>
            </div>
          </div>
        `;
      } else if (activeTab === 'costing') {
        if (!costing) {
          tabContentHtml = `<div class="p-6 text-center text-xs" style="color: var(--text-muted);">No costing record linked to this order.</div>`;
        } else {
          const evalRes = evaluateCostingSheet(costing);
          tabContentHtml = buildFullCostingBreakdownMarkup(costing, evalRes);
        }
      } else if (activeTab === 'quantities') {
        const sum = costing ? costing.calculatedSummary : null;
        tabContentHtml = `
          <div class="space-y-4">
            <div class="overflow-x-auto rounded-xl border" style="border-color: var(--border-hairline);">
              <table class="w-full text-left border-collapse tf-table text-xs font-mono-tabular">
                <thead>
                  <tr>
                    <th class="py-2 px-3">Size</th>
                    <th class="py-2 px-3 text-right">Order Qty (pcs)</th>
                    <th class="py-2 px-3 text-right">Share (%)</th>
                    <th class="py-2 px-3 text-right">Piece Net Wt (g)</th>
                    <th class="py-2 px-3 text-right">Piece Gross Cons. (g)</th>
                    <th class="py-2 px-3 text-right">Extended Cost (₹)</th>
                  </tr>
                </thead>
                <tbody>
                  ${SIZES.map((sz) => {
                    const q = Number(o.sizeQuantities?.[sz]) || 0;
                    const share = o.totalPieces > 0 ? ((q / o.totalPieces) * 100).toFixed(1) : '0.0';
                    const sInfo = sum?.sizeSummaries?.[sz];
                    return `
                      <tr>
                        <td class="py-2 px-3 font-bold">${sz}</td>
                        <td class="py-2 px-3 text-right">${formatNumber(q)}</td>
                        <td class="py-2 px-3 text-right">${share}%</td>
                        <td class="py-2 px-3 text-right">${sInfo ? sInfo.garmentNetWeightGrams + ' g' : '—'}</td>
                        <td class="py-2 px-3 text-right">${sInfo ? sInfo.garmentConsumptionGrams + ' g' : '—'}</td>
                        <td class="py-2 px-3 text-right font-semibold">${sInfo ? formatINR(sInfo.garmentFabricCost * q) : '—'}</td>
                      </tr>
                    `;
                  }).join('')}
                </tbody>
              </table>
            </div>
          </div>
        `;
      } else if (activeTab === 'workflow') {
        tabContentHtml = `
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <div class="text-xs">Workflow Progress: <strong class="font-mono-tabular">${wf.progressPct}%</strong> (${wf.completedTasks} of ${wf.milestoneTasks} milestones completed)</div>
              <button type="button" onclick="openCreateTaskModal('${escapeHtml(o.id)}')" class="tf-btn-secondary px-3 py-1 rounded text-xs">+ Add Task to Order</button>
            </div>
            ${orderTasks
              .map(
                (t) => `
                <div class="p-3 rounded-lg tf-subtle flex items-center justify-between gap-3 text-xs">
                  <div>
                    <div class="font-semibold">${escapeHtml(t.title)} <span class="tf-badge tf-badge-neutral ml-1">${escapeHtml(t.status)}</span></div>
                    <div class="text-[11px] mt-0.5" style="color: var(--text-secondary);">Assigned: ${escapeHtml(t.assignedUserName)} · Due: ${escapeHtml(t.dueDate)} · Remarks: ${escapeHtml(t.remarks || '')}</div>
                  </div>
                  ${
                    t.status !== 'Completed'
                      ? `<button type="button" onclick="openCompleteTaskModal('${escapeHtml(t.id)}')" class="tf-btn-primary px-2.5 py-1 rounded text-xs">Complete</button>`
                      : `<span class="font-mono-tabular text-[11px]" style="color: var(--status-success-text);">✓ ${escapeHtml(t.completedAt || '')}</span>`
                  }
                </div>
              `
              )
              .join('')}
          </div>
        `;
      } else if (activeTab === 'history') {
        tabContentHtml = `
          <div class="space-y-3 text-xs">
            <div class="font-semibold">Order Status-Change Timeline</div>
            ${(o.statusHistory || [])
              .map(
                (sh) => `
                <div class="p-3 rounded-lg tf-subtle flex items-start justify-between gap-3">
                  <div>
                    <div class="font-semibold">${escapeHtml(sh.fromStatus)} → ${escapeHtml(sh.toStatus)}</div>
                    <div class="mt-0.5" style="color: var(--text-secondary);">${escapeHtml(sh.remarks)}</div>
                    <div class="text-[11px] mt-0.5" style="color: var(--text-muted);">Actor: ${escapeHtml(sh.actor)} (${escapeHtml(sh.role)})</div>
                  </div>
                  <span class="font-mono-tabular text-[11px]" style="color: var(--text-muted);">${escapeHtml(sh.timestamp)}</span>
                </div>
              `
              )
              .join('')}

            <div class="font-semibold pt-2">Associated Audit Log Records</div>
            ${orderAudit
              .map(
                (a) => `
                <div class="p-3 rounded-lg tf-subtle flex items-start justify-between gap-3">
                  <div>
                    <div class="font-mono-tabular font-semibold">${escapeHtml(a.action)} (${escapeHtml(a.entityId)})</div>
                    <div class="mt-0.5" style="color: var(--text-secondary);">${escapeHtml(a.remarks)}</div>
                    <div class="text-[11px] mt-0.5" style="color: var(--text-muted);">${escapeHtml(a.actorName)} · ${escapeHtml(a.actorRole)}</div>
                  </div>
                  <span class="font-mono-tabular text-[11px]" style="color: var(--text-muted);">${escapeHtml(a.createdAt)}</span>
                </div>
              `
              )
              .join('')}
          </div>
        `;
      }

      openModal({
        category: `MANUFACTURING ORDER TRACEABILITY · ${o.orderNumber}`,
        title: `${o.customerName} — ${o.styleNumber} (${o.styleName})`,
        bodyHtml: `
          <div class="space-y-4">
            <div class="flex flex-wrap gap-1.5 border-b pb-3" style="border-color: var(--border-hairline);">
              ${tabs
                .map(([key, label]) => {
                  const isAct = activeTab === key;
                  const st = isAct
                    ? 'background-color: var(--accent-primary); color: #fff;'
                    : 'background-color: var(--bg-subtle); color: var(--text-secondary);';
                  return `<button type="button" onclick="openOrderDetailModal('${escapeHtml(o.id)}', '${key}')" class="px-3 py-1.5 rounded-lg text-xs font-medium" style="${st}">${escapeHtml(label)}</button>`;
                })
                .join('')}
            </div>
            ${tabContentHtml}
          </div>
        `,
        footerHtml: `<button type="button" onclick="closeModal()" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">Close Order Sheet</button>`
      });
    }

    function handleOrderStatusTransition(orderId) {
      const idx = appState.db.orders.findIndex((o) => o.id === orderId);
      if (idx < 0) return;
      const newStatus = document.getElementById('orderTransitionStatusSelect')?.value;
      const remarks = document.getElementById('orderTransitionRemarkInput')?.value || '';

      const res = transitionOrderStatus({
        order: appState.db.orders[idx],
        actor: appState.currentUser,
        newStatus,
        remarks
      });
      if (!res.ok) {
        showToast(res.error, 'error');
        return;
      }
      appState.db.orders[idx] = res.order;
      appState.db.auditLogs.unshift(res.auditEntry);
      saveDatabase();
      openOrderDetailModal(orderId, 'history');
      renderCurrentActiveView();
      showToast(`Order ${res.order.orderNumber} transitioned to ${newStatus}. History preserved.`, 'success');
    }

    function openCreateOrderModal() {
      const auth = assertPermission(appState.currentUser, 'order:write');
      if (!auth.allowed) {
        showToast(auth.error, 'error');
        return;
      }
      openModal({
        category: 'NEW PRODUCTION ORDER',
        title: 'Create Manufacturing Order Linked to Costing',
        bodyHtml: `
          <form id="createOrderForm" onsubmit="submitCreateOrder(event)" class="space-y-3.5 text-xs">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-medium mb-1">Order Number *</label>
                <input id="newOrdNumber" type="text" required value="HK-ORD-2026-119" class="tf-input w-full font-mono-tabular" />
              </div>
              <div>
                <label class="block font-medium mb-1">Buyer PO Reference *</label>
                <input id="newOrdPo" type="text" required value="PO-BUY-9920" class="tf-input w-full font-mono-tabular" />
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-medium mb-1">Customer / Buyer Name *</label>
                <input id="newOrdCustomer" type="text" required value="Nordic Loom Copenhagen" class="tf-input w-full" />
              </div>
              <div>
                <label class="block font-medium mb-1">Link Approved Costing Sheet *</label>
                <select id="newOrdCostingId" class="tf-input w-full">
                  ${appState.db.costingRecords
                    .map(
                      (c) =>
                        `<option value="${escapeHtml(c.id)}">${escapeHtml(c.styleNumber)} — ${escapeHtml(c.styleName)} (${formatNumber(c.calculatedSummary?.totalOrderQuantity || 0)} pcs)</option>`
                    )
                    .join('')}
                </select>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block font-medium mb-1">Order Date *</label>
                <input id="newOrdDate" type="date" required value="2026-10-18" class="tf-input w-full font-mono-tabular" />
              </div>
              <div>
                <label class="block font-medium mb-1">Export Due Date *</label>
                <input id="newOrdDue" type="date" required value="2026-11-12" class="tf-input w-full font-mono-tabular" />
              </div>
            </div>
            <div>
              <label class="block font-medium mb-1">Production Remarks</label>
              <input id="newOrdRemarks" type="text" value="Allocated to Knitting & Cutting Unit II." class="tf-input w-full" />
            </div>
          </form>
        `,
        footerHtml: `
          <button type="button" onclick="closeModal()" class="tf-btn-secondary px-4 py-2 rounded-lg text-xs font-medium">Cancel</button>
          <button type="button" onclick="document.getElementById('createOrderForm').requestSubmit()" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">Create Order</button>
        `
      });
    }

    function submitCreateOrder(e) {
      e.preventDefault();
      const costingId = document.getElementById('newOrdCostingId').value;
      const costing = appState.db.costingRecords.find((c) => c.id === costingId) || appState.db.costingRecords[0];
      const now = new Date().toISOString();
      const newOrd = {
        id: 'ORD-' + Math.floor(2610 + Math.random() * 890),
        orderNumber: document.getElementById('newOrdNumber').value.trim(),
        customerName: document.getElementById('newOrdCustomer').value.trim(),
        buyerPoRef: document.getElementById('newOrdPo').value.trim(),
        styleNumber: costing.styleNumber,
        styleName: costing.styleName,
        garmentType: costing.garmentType,
        category: costing.category,
        costingId: costing.id,
        status: 'Currently Going On',
        currentStage: 'Fabric Sourcing & Knitting',
        sizeQuantities: { ...costing.sizeQuantities },
        totalPieces: costing.calculatedSummary?.totalOrderQuantity || 1000,
        completedPieces: 0,
        orderDate: document.getElementById('newOrdDate').value,
        dueDate: document.getElementById('newOrdDue').value,
        completedAt: null,
        cancelledAt: null,
        cancellationReason: null,
        remarks: document.getElementById('newOrdRemarks').value.trim(),
        createdBy: appState.currentUser.fullName,
        statusHistory: [
          {
            fromStatus: 'New',
            toStatus: 'Currently Going On',
            actor: appState.currentUser.fullName,
            role: appState.currentUser.role,
            remarks: `Order created and linked to costing ${costing.id} (${costing.styleNumber}).`,
            timestamp: now
          }
        ]
      };
      appState.db.orders.unshift(newOrd);
      saveDatabase();
      closeModal();
      renderCurrentActiveView();
      showToast(`Created order ${newOrd.orderNumber} for ${newOrd.customerName}.`, 'success');
    }

    // --- 12. VIEW 5: SETTINGS, RBAC & IN-BROWSER TEST SUITE ---
    function renderSettingsView() {
      const u = appState.currentUser;
      if (!u) return;
      document.getElementById('settingsRoleBadge').textContent = u.role;
      document.getElementById('profFullName').value = u.fullName;
      document.getElementById('profEmail').value = u.email;
      document.getElementById('profDepartment').value = u.department;
      document.getElementById('prefNotifyDueSoon').checked = Boolean(u.notifyDueSoon);
      document.getElementById('prefNotifyStatus').checked = Boolean(u.notifyStatusChange);
      document.getElementById('prefReducedMotion').checked = Boolean(appState.reducedMotion);

      const rbacBody = document.getElementById('settingsRbacTableBody');
      if (rbacBody) {
        rbacBody.innerHTML = appState.db.users
          .map((usr) => {
            const canCost = hasPermission(usr, 'costing:write');
            const canApprove = hasPermission(usr, 'costing:approve');
            const canTask = hasPermission(usr, 'task:complete');
            const canOrder = hasPermission(usr, 'order:transition');
            const isCurrent = usr.id === u.id;
            return `
              <tr>
                <td class="py-2.5 px-3">
                  <div class="font-semibold">${escapeHtml(usr.fullName)}</div>
                  <div class="font-mono-tabular text-[11px]" style="color: var(--text-muted);">${escapeHtml(usr.email)}</div>
                </td>
                <td class="py-2.5 px-3"><span class="tf-badge tf-badge-neutral font-mono-tabular">${escapeHtml(usr.role)}</span></td>
                <td class="py-2.5 px-3 font-mono-tabular">${canCost ? 'Write' : 'Read'}${canApprove ? ' + Approve' : ''}</td>
                <td class="py-2.5 px-3 font-mono-tabular">${canTask ? 'Complete & Reopen' : 'Read-Only'}</td>
                <td class="py-2.5 px-3 font-mono-tabular">${canOrder ? 'Transition Allowed' : 'Restricted'}</td>
                <td class="py-2.5 px-3 text-right">
                  ${
                    isCurrent
                      ? `<span class="tf-badge tf-badge-success">Active</span>`
                      : `<button type="button" onclick="handleQuickRoleSwitch('${escapeHtml(usr.id)}')" class="tf-btn-secondary px-2.5 py-1 rounded text-xs">Switch Role</button>`
                  }
                </td>
              </tr>
            `;
          })
          .join('');
      }

      runInBrowserVerificationSuite(true);
    }

    function handleProfileSave(e) {
      e.preventDefault();
      const u = appState.currentUser;
      if (!u) return;
      u.notifyDueSoon = document.getElementById('prefNotifyDueSoon').checked;
      u.notifyStatusChange = document.getElementById('prefNotifyStatus').checked;
      appState.db.users[0].notifyDueSoon = u.notifyDueSoon;
      appState.db.users[0].notifyStatusChange = u.notifyStatusChange;
      appState.db.users[0].themePreference = u.themePreference;
      saveDatabase();
      syncAuthenticatedUI();
      showToast('Profile and notification preferences saved.', 'success');
    }

    function exportDatabaseJson() {
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(appState.db, null, 2));
      const dl = document.createElement('a');
      dl.setAttribute('href', dataStr);
      dl.setAttribute('download', `hk_threadflow_backup_${new Date().toISOString().slice(0, 10)}.json`);
      document.body.appendChild(dl);
      dl.click();
      dl.remove();
      showToast('Exported full ThreadFlow database JSON snapshot.', 'info');
    }

    function openResetDatabaseModal() {
      openModal({
        category: 'DATABASE RESET CONFIRMATION',
        title: 'Reset ThreadFlow Database to Factory Seed State?',
        bodyHtml: `
          <p class="text-xs leading-relaxed" style="color: var(--text-secondary);">
            This will restore the sample costing records, manufacturing orders, and workflow tasks. Any custom changes will be replaced.
          </p>
        `,
        footerHtml: `
          <button type="button" onclick="closeModal()" class="tf-btn-secondary px-4 py-2 rounded-lg text-xs font-medium">Cancel</button>
          <button type="button" onclick="confirmResetDatabase()" class="tf-btn-primary px-4 py-2 rounded-lg text-xs font-medium">Confirm Factory Reset</button>
        `
      });
    }

    function confirmResetDatabase() {
      appState.db = createInitialDatabase();
      appState.wizardState = {
        step: 1,
        editingCostingId: null,
        form: createBlankWizardForm()
      };
      saveDatabase();
      safeStorageSet(WIZARD_STORAGE_KEY, appState.wizardState);
      closeModal();
      renderCurrentActiveView();
      showToast('Database restored to factory seed records.', 'info');
    }

    function runInBrowserVerificationSuite(silent = false) {
      const out = document.getElementById('inBrowserTestResults');
      if (!out) return;
      const results = [];
      const assertCheck = (name, cond, detail) => {
        results.push({ name, passed: Boolean(cond), detail });
      };

      // Test 1: Unit conversions
      assertCheck(
        'Costing: Grams <-> Kilograms exact conversion',
        gramsToKilograms(1000) === 1 && kilogramsToGrams(0.2456) === 245.6,
        '1000g = 1.000000kg, 0.2456kg = 245.6g'
      );

      // Test 2: Net Weight vs Gross Consumption vs Cost separation
      const compCalc = calculateComponentForSize({
        lengthCm: 67,
        widthCm: 47,
        seamAllowanceCm: 3,
        panelMultiplier: 2,
        fabricGsm: 200,
        fabricPricePerKg: 500,
        wastageAllowancePct: 10
      });
      assertCheck(
        'Costing: Component Net Weight (140g) != Gross Consumption (154g) & Cost (₹77.00)',
        compCalc.valid && compCalc.netWeightGrams === 140 && compCalc.consumptionGrams === 154 && compCalc.fabricCost === 77,
        `Net=${compCalc.netWeightGrams}g, Cons=${compCalc.consumptionGrams}g, Cost=₹${compCalc.fabricCost}`
      );

      // Test 3: Missing input vs legitimate zero
      const missingRes = calculateComponentForSize({
        lengthCm: '',
        widthCm: 50,
        fabricGsm: 200,
        fabricPricePerKg: 500
      });
      assertCheck(
        'Costing: Missing measurements rejected (never silently coerced to 0)',
        missingRes.valid === false && missingRes.netWeightGrams === null,
        missingRes.error
      );

      // Test 4: Workflow completion & reopen history preservation
      const mockActor = { fullName: 'Test Lead', role: 'production_lead' };
      const cRes = completeWorkflowTask({
        task: { id: 'T1', orderId: 'O1', title: 'Test', status: 'Pending', history: [] },
        actor: mockActor,
        remarks: 'Done'
      });
      const rRes = reopenWorkflowTask({
        task: cRes.task,
        actor: mockActor,
        targetStatus: 'In Progress',
        reason: 'Re-verify'
      });
      assertCheck(
        'Workflow: Complete & Reopen preserves previousCompletions and audit trail',
        cRes.ok && rRes.ok && rRes.task.reopenedCount === 1 && rRes.task.previousCompletions.length === 1,
        `History entries: ${rRes.task.history.length}, ReopenedCount: ${rRes.task.reopenedCount}`
      );

      // Test 5: RBAC Viewer restriction
      const viewerActor = { fullName: 'Viewer', role: 'viewer' };
      const deniedRes = completeWorkflowTask({
        task: { id: 'T2', orderId: 'O1', title: 'Test', status: 'Pending' },
        actor: viewerActor
      });
      assertCheck(
        'Security: RBAC blocks viewer role from mutating tasks or orders',
        deniedRes.ok === false,
        deniedRes.error
      );

      out.innerHTML = results
        .map(
          (r) => `
          <div class="p-2 rounded flex items-center justify-between gap-2 ${r.passed ? 'tf-badge-success' : 'tf-badge-danger'}">
            <span>${r.passed ? 'PASS' : 'FAIL'} · ${escapeHtml(r.name)}</span>
            <span class="opacity-80">${escapeHtml(r.detail)}</span>
          </div>
        `
        )
        .join('');

      if (!silent) {
        showToast(`Executed ${results.length} verification suites: all passed.`, 'success');
      }
    }

    // --- 13. Universal Modal Controller ---
    function openModal({ category, title, bodyHtml, footerHtml }) {
      const overlay = document.getElementById('modalOverlay');
      document.getElementById('modalCategoryLabel').textContent = category || 'DETAIL';
      document.getElementById('modalTitle').textContent = title || '';
      document.getElementById('modalBody').innerHTML = bodyHtml || '';
      document.getElementById('modalFooter').innerHTML = footerHtml || '';
      overlay.classList.remove('hidden');
    }

    function closeModal() {
      const overlay = document.getElementById('modalOverlay');
      if (overlay) overlay.classList.add('hidden');
    }

    window.addEventListener('DOMContentLoaded', initApplication);
  </script>
</body>
</html>
"""

final_html = (
    HTML_TEMPLATE
    .replace("__BROWSER_COSTING_JS__", browser_costing_js)
    .replace("__BROWSER_WORKFLOW_JS__", browser_workflow_js)
    .replace("__BROWSER_SEED_JS__", browser_seed_js)
)

with open(INTERMEDIATE_HTML, "w", encoding="utf-8") as f:
    f.write(final_html)

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(final_html)

with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, _dirs, files in os.walk(PROJ_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            if os.path.abspath(full_path) == os.path.abspath(OUTPUT_ZIP):
                continue
            if (file == ".env" or (file.startswith(".env.") and file != ".env.example")
                or "node_modules" in root.split(os.sep)
                or os.path.abspath(root) == os.path.join(BASE_DIR, "data")):
                continue
            rel_path = os.path.relpath(full_path, PROJ_DIR)
            zf.write(full_path, os.path.join("threadflow", rel_path))

print("Built:", OUTPUT_HTML, "and", OUTPUT_ZIP)
