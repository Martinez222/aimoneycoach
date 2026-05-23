const translations = {
  ro: {
    "auth.title": "Finante personale, fara batai de cap.",
    "auth.lede": "Intri, completezi cateva date si apoi vorbesti cu un coach financiar personalizat. Restul se intampla in fundal.",
    "auth.loginTab": "Login",
    "auth.registerTab": "Cont nou",
    "auth.fullName": "Nume",
    "auth.fullNamePlaceholder": "Ex: Andrei Popescu",
    "auth.email": "Email",
    "auth.emailPlaceholder": "tu@exemplu.ro",
    "auth.password": "Parola",
    "auth.passwordPlaceholder": "Parola ta",
    "auth.helper": "Dupa autentificare, profilul si chat-ul apar pe aceeasi pagina.",
    "auth.submitLogin": "Intra",
    "auth.submitRegister": "Creeaza cont",
    "auth.processing": "Se proceseaza...",
    "auth.success": "Autentificare reusita.",
    "dashboard.kicker": "Tablou de bord",
    "dashboard.welcome": "Bun venit,",
    "dashboard.logout": "Logout",
    "dashboard.clearData": "Sterge toate datele",
    "dashboard.clearConfirm": "Sigur vrei sa stergi toate datele salvate? Contul tau va ramane activ.",
    "dashboard.clearing": "Stergem toate datele...",
    "dashboard.cleared": "Toate datele salvate au fost sterse.",
    "dashboard.aiEnabled": "AI activ",
    "dashboard.aiFallback": "Fallback local",
    "profile.kicker": "Date editabile",
    "profile.title": "Profil financiar",
    "profile.hint": "Separi fondul de urgenta de economiile pentru obiective, apoi chat-ul devine personalizat.",
    "profile.income": "Venit lunar",
    "profile.expenses": "Cheltuieli lunare",
    "profile.age": "Varsta",
    "profile.creditGender": "Sex pentru eligibilitate credit",
    "profile.genderMale": "Barbat",
    "profile.genderFemale": "Femeie",
    "profile.emergencyKicker": "Buffer de siguranta",
    "profile.emergencyTitle": "Ce fond de urgenta ai acum?",
    "profile.emergencyHint": "Separat de vacante, investitii si alte obiective.",
    "profile.emergencyFund": "Fond de urgenta separat",
    "profile.emergencyNote": "Pune aici doar banii pastrati pentru cheltuieli neprevazute, nu economiile pentru vacanta, casa sau investitii.",
    "profile.emergencyPreviewDefault": "Completeaza datele si vezi instant cate luni acoperi.",
    "profile.emergencyPreviewCurrent": "Acum acoperi aproximativ {current} luni.",
    "profile.emergencyPreviewTarget": "Tinta estimata este {target} luni, adica aproximativ {amount} RON.",
    "profile.emergencyPreviewShortfall": "Iti mai lipsesc aproximativ {amount} RON pentru bufferul recomandat.",
    "profile.emergencyPreviewReady": "Fondul tau de urgenta este deja in zona recomandata.",
    "profile.savings": "Economii pentru obiective",
    "profile.debts": "Datorii",
    "profile.riskProfile": "Profil de risc",
    "profile.riskConservative": "Conservator",
    "profile.riskModerate": "Moderat",
    "profile.riskAggressive": "Agresiv",
    "profile.goals": "Obiective",
    "profile.goalsPlaceholder": "emergency_fund, investing, retirement",
    "profile.save": "Salveaza datele",
    "profile.saving": "Salvam datele...",
    "profile.saved": "Profil salvat. Planul a fost actualizat automat.",
    "goal.quickKicker": "Obiectiv rapid",
    "goal.quickTitle": "Vreau un plan pentru ceva concret",
    "goal.name": "Obiectiv",
    "goal.namePlaceholder": "Ex: vacanta",
    "goal.amount": "Suma dorita",
    "goal.currency": "Moneda",
    "goal.months": "In cate luni?",
    "goal.allowCredit": "Daca lipseste ceva, cauta si variante de finantare",
    "goal.generate": "Genereaza planul",
    "goal.generating": "Construim planul...",
    "goal.generated": "Planul obiectivului a fost generat.",
    "goal.feasible": "Obiectivul pare realizabil fara credit.",
    "goal.gap": "Iti mai lipsesc aproximativ {amount} lei.",
    "goal.chipSavings": "Poti economisi cam {amount} lei/luna.",
    "goal.chipAvailable": "Disponibil acum pentru obiectiv: {amount} lei.",
    "goal.chipProjected": "Poti ajunge la aproximativ {amount} lei pana la termen.",
    "goal.chipEmergency": "Fond minim de urgenta de pastrat: {amount} lei.",
    "goal.chipSafe": "{provider}: {product} cu {rate}% pe an.",
    "goal.chipLoan": "{provider}: {product}, DAE {rate}%, rata realista ~{payment} lei/luna.",
    "goal.chipInvestment": "{product}: cotatie indicativa {price} {currency}.",
    "goal.scoreTitle": "Scor de realizare",
    "goal.scoreDefault": "Genereaza un plan pentru a vedea cat de realizabil este obiectivul.",
    "goal.pieKicker": "Placinta obiective",
    "goal.pieTitle": "Harta banilor tai",
    "goal.pieEmpty": "Obiectivele apar aici dupa primul plan generat.",
    "goal.simulatorKicker": "Simulator",
    "goal.simulatorTitle": "Ce se intampla daca mai poti economisi?",
    "goal.simulatorLabel": "Extra economisire lunara",
    "goal.simulatorHint": "Muta sliderul dupa ce generezi primul plan.",
    "goal.simulatorHintActive": "Planul se recalculeaza instant pe baza sliderului.",
    "goal.simulatorValue": "+{amount} RON/luna",
    "goal.variantsKicker": "3 variante de plan",
    "goal.variantsTitle": "Alege ritmul care ti se potriveste",
    "goal.variantRecommended": "Recomandata",
    "goal.variantScore": "Scor",
    "goal.variantMonthly": "Efort lunar",
    "goal.variantProjected": "Total estimat",
    "goal.variantTimeline": "Luni estimate",
    "goal.variantEmergency": "Buffer pastrat",
    "goal.variantGap": "Gap",
    "goal.variantOnTrack": "In grafic",
    "goal.variantUsesCredit": "Poate folosi finantare",
    "goal.variantNoCredit": "Fara finantare",
    "goal.variantInstrument": "Instrument cheie",
    "goal.marketKicker": "Piata verificata",
    "goal.marketTitle": "Comparatie intre banci",
    "goal.marketSummary": "Am verificat top {scopeCount} banci mari din Romania pentru {family} si am gasit {offerCount} oferte publice care se pot compara cu bugetul tau.",
    "goal.marketBanks": "Banci verificate: {banks}",
    "goal.marketFallbackFamily": "finantarea potrivita",
    "overview.kicker": "In fundal",
    "overview.title": "Rezumat automat",
    "overview.healthScore": "Scor financiar",
    "overview.riskScore": "Scor risc",
    "overview.savingsCapacity": "Economii lunare",
    "overview.emergencyFund": "Fond urgenta",
    "overview.aboutYou": "Ce intelege aplicatia despre tine",
    "overview.yourPlan": "Planul tau",
    "overview.goalPlan": "Plan pentru obiectiv",
    "overview.nextActions": "Ce faci mai departe",
    "overview.defaultSnapshot": "Completeaza profilul pentru a vedea rezumatul automat.",
    "overview.defaultPlan": "Dupa salvare, planul se genereaza automat.",
    "overview.defaultNextStep": "Completeaza profilul pentru a porni.",
    "overview.defaultGoalSummary": "Exemplu: vacanta de 9000 lei in 6 luni.",
    "disclaimer.goal": "Disclaimer: acest plan este orientativ. Ofertele, costurile si randamentele se pot schimba si trebuie verificate la sursa inainte de orice decizie.",
    "disclaimer.chat": "Disclaimer: raspunsurile personalizate sunt doar informative si educative si nu inlocuiesc consultanta financiara, fiscala, juridica sau investitionala.",
    "offers.safe": "Economisire si titluri de stat",
    "offers.funds": "Fonduri si ETF-uri",
    "offers.stocks": "Actiuni",
    "offers.loans": "Finantare pentru diferenta",
    "offers.brokers": "Brokeri pentru ETF-uri si actiuni",
    "offers.safeEmpty": "Pentru acest termen nu am gasit acum o oferta prudenta mai potrivita decat economisirea clasica.",
    "offers.fundsEmpty": "Pentru obiectivul acesta nu are sens sa adaugi acum fonduri sau ETF-uri mai riscante.",
    "offers.stocksEmpty": "Actiunile individuale apar doar pentru profil mai agresiv si orizont mai lung.",
    "offers.brokersEmpty": "Brokerii apar aici cand planul include ETF-uri, fonduri sau actiuni care trebuie executate printr-o platforma de tranzactionare.",
    "offers.loansEmpty": "Nu este nevoie de finantare externa pentru acest obiectiv.",
    "offers.loansNotRealistic": "Nu exista inca o oferta de credit care sa se incadreze realist in bugetul tau pentru acest gap.",
    "offers.source": "Sursa: {source}",
    "offers.perYear": "{value}% pe an",
    "offers.apr": "DAE {value}%",
    "offers.monthlyPayment": "rata ~{value} {currency}/luna",
    "offers.paymentCap": "plafon profil ~{value} {currency}/luna",
    "offers.affordableAmount": "finantare realista ~{value} {currency}",
    "offers.remainingGap": "raman descoperiti ~{value} {currency}",
    "offers.fullCoverage": "poate acoperi integral suma analizata",
    "offers.partialCoverage": "acopera doar partial suma analizata",
    "offers.quote": "cotatie ~{value} {currency}",
    "offers.minimumFrom": "minim {value} {currency}",
    "offers.costAnnual": "cost anual ~{value}%",
    "offers.costTransaction": "cost tranzactionare ~{value}%",
    "offers.costFx": "FX ~{value}%",
    "offers.costSubscription": "subscriere {value}%",
    "offers.costRedemption": "rascumparare {value}%",
    "offers.costCustody": "custodie {value}%",
    "offers.costLabel": "Costuri",
    "chat.kicker": "Chat personalizat",
    "chat.title": "Intreaba direct",
    "chat.hint": "Raspunsurile folosesc profilul si planul tau.",
    "chat.placeholder": "Ex: Vreau o vacanta de 9000 lei in 6 luni. Ce fac?",
    "chat.send": "Trimite",
    "chat.empty": "Salut! Dupa ce completezi profilul, iti raspund pe baza situatiei tale financiare.",
    "chat.answering": "Coach-ul raspunde...",
    "chat.fallback": "Raspuns generat local.",
    "chat.ai": "Raspuns generat cu AI.",
    "chat.error": "Nu am reusit sa raspund acum. Incearca din nou.",
    "pwa.install": "Instaleaza aplicatia",
    "pwa.installReady": "Poti instala aplicatia pe telefon sau desktop direct din browser.",
    "pwa.installing": "Pregatim instalarea...",
    "pwa.installed": "Aplicatia a fost instalata.",
    "pwa.installIos": "Pe iPhone sau iPad, foloseste Share si apoi Add to Home Screen.",
    "pwa.online": "Online",
    "pwa.offline": "Offline",
    "pwa.offlineTitle": "Mod offline activ",
    "pwa.offlineBody": "Vezi ultima stare salvata pe acest dispozitiv. Chat-ul si ofertele live revin cand ai internet.",
    "pwa.offlineCached": "Esti offline. Iti arat ultima stare salvata pe acest dispozitiv.",
    "pwa.backOnline": "Conexiunea a revenit. Datele live se pot actualiza din nou.",
    "common.user": "utilizator",
    "common.error": "A aparut o eroare.",
    "common.years.one": "an",
    "common.years.other": "ani",
    "common.months": "luni",
    "common.none": "-",
  },
  en: {
    "auth.title": "Personal finance, without the headache.",
    "auth.lede": "Sign in, fill in a few details, then talk to a personalized financial coach. The rest happens in the background.",
    "auth.loginTab": "Login",
    "auth.registerTab": "New account",
    "auth.fullName": "Name",
    "auth.fullNamePlaceholder": "Ex: Andrew Popescu",
    "auth.email": "Email",
    "auth.emailPlaceholder": "you@example.com",
    "auth.password": "Password",
    "auth.passwordPlaceholder": "Your password",
    "auth.helper": "After login, your profile and chat appear on the same page.",
    "auth.submitLogin": "Sign in",
    "auth.submitRegister": "Create account",
    "auth.processing": "Processing...",
    "auth.success": "Authentication successful.",
    "dashboard.kicker": "Dashboard",
    "dashboard.welcome": "Welcome,",
    "dashboard.logout": "Logout",
    "dashboard.clearData": "Delete all data",
    "dashboard.clearConfirm": "Are you sure you want to delete all saved data? Your account will remain active.",
    "dashboard.clearing": "Deleting all saved data...",
    "dashboard.cleared": "All saved data has been deleted.",
    "dashboard.aiEnabled": "AI enabled",
    "dashboard.aiFallback": "Local fallback",
    "profile.kicker": "Editable data",
    "profile.title": "Financial profile",
    "profile.hint": "Keep your emergency fund separate from goal savings, then the chat becomes personalized.",
    "profile.income": "Monthly income",
    "profile.expenses": "Monthly expenses",
    "profile.age": "Age",
    "profile.creditGender": "Sex used for credit eligibility",
    "profile.genderMale": "Male",
    "profile.genderFemale": "Female",
    "profile.emergencyKicker": "Safety buffer",
    "profile.emergencyTitle": "How much emergency fund do you have now?",
    "profile.emergencyHint": "Separate from vacations, investing, and other goals.",
    "profile.emergencyFund": "Separate emergency fund",
    "profile.emergencyNote": "Put here only the money reserved for unexpected expenses, not the savings for vacations, a home, or investing.",
    "profile.emergencyPreviewDefault": "Fill in the numbers and instantly see how many months you cover.",
    "profile.emergencyPreviewCurrent": "You currently cover about {current} months.",
    "profile.emergencyPreviewTarget": "Your estimated target is {target} months, or about {amount} RON.",
    "profile.emergencyPreviewShortfall": "You are still short by about {amount} RON for the recommended buffer.",
    "profile.emergencyPreviewReady": "Your emergency fund is already within the recommended zone.",
    "profile.savings": "Goal savings",
    "profile.debts": "Debts",
    "profile.riskProfile": "Risk profile",
    "profile.riskConservative": "Conservative",
    "profile.riskModerate": "Moderate",
    "profile.riskAggressive": "Aggressive",
    "profile.goals": "Goals",
    "profile.goalsPlaceholder": "emergency_fund, investing, retirement",
    "profile.save": "Save data",
    "profile.saving": "Saving data...",
    "profile.saved": "Profile saved. The plan was updated automatically.",
    "goal.quickKicker": "Quick goal",
    "goal.quickTitle": "I want a plan for something specific",
    "goal.name": "Goal",
    "goal.namePlaceholder": "Ex: vacation",
    "goal.amount": "Target amount",
    "goal.currency": "Currency",
    "goal.months": "In how many months?",
    "goal.allowCredit": "If there is a gap, also search financing options",
    "goal.generate": "Generate plan",
    "goal.generating": "Building your plan...",
    "goal.generated": "The goal plan has been generated.",
    "goal.feasible": "The goal looks achievable without credit.",
    "goal.gap": "You are still missing about {amount} RON.",
    "goal.chipSavings": "You can save about {amount} RON/month.",
    "goal.chipAvailable": "Available now for this goal: {amount} RON.",
    "goal.chipProjected": "You could reach about {amount} RON by the deadline.",
    "goal.chipEmergency": "Minimum emergency fund to keep: {amount} RON.",
    "goal.chipSafe": "{provider}: {product} at {rate}% per year.",
    "goal.chipLoan": "{provider}: {product}, APR {rate}%, realistic payment ~{payment} RON/month.",
    "goal.chipInvestment": "{product}: indicative quote {price} {currency}.",
    "goal.scoreTitle": "Achievement score",
    "goal.scoreDefault": "Generate a plan to see how achievable your goal is.",
    "goal.pieKicker": "Objective pie",
    "goal.pieTitle": "Your money map",
    "goal.pieEmpty": "Your objectives will appear here after the first generated plan.",
    "goal.simulatorKicker": "Simulator",
    "goal.simulatorTitle": "What happens if you can save more?",
    "goal.simulatorLabel": "Extra monthly saving",
    "goal.simulatorHint": "Move the slider after you generate the first plan.",
    "goal.simulatorHintActive": "The plan recalculates instantly based on the slider.",
    "goal.simulatorValue": "+{amount} RON/month",
    "goal.variantsKicker": "3 plan variants",
    "goal.variantsTitle": "Choose the pace that fits you",
    "goal.variantRecommended": "Recommended",
    "goal.variantScore": "Score",
    "goal.variantMonthly": "Monthly effort",
    "goal.variantProjected": "Projected total",
    "goal.variantTimeline": "Estimated months",
    "goal.variantEmergency": "Emergency kept",
    "goal.variantGap": "Gap",
    "goal.variantOnTrack": "On track",
    "goal.variantUsesCredit": "Can use financing",
    "goal.variantNoCredit": "No financing",
    "goal.variantInstrument": "Core instrument",
    "goal.marketKicker": "Market checked",
    "goal.marketTitle": "Bank comparison",
    "goal.marketSummary": "I checked the top {scopeCount} major Romanian banks for {family} and found {offerCount} public offers that still fit your budget.",
    "goal.marketBanks": "Banks checked: {banks}",
    "goal.marketFallbackFamily": "the relevant financing type",
    "overview.kicker": "In the background",
    "overview.title": "Automatic summary",
    "overview.healthScore": "Financial score",
    "overview.riskScore": "Risk score",
    "overview.savingsCapacity": "Monthly savings",
    "overview.emergencyFund": "Emergency fund",
    "overview.aboutYou": "What the app understands about you",
    "overview.yourPlan": "Your plan",
    "overview.goalPlan": "Goal plan",
    "overview.nextActions": "What to do next",
    "overview.defaultSnapshot": "Complete your profile to see the automatic summary.",
    "overview.defaultPlan": "After saving, the plan is generated automatically.",
    "overview.defaultNextStep": "Complete your profile to get started.",
    "overview.defaultGoalSummary": "Example: a 9000 RON vacation in 6 months.",
    "disclaimer.goal": "Disclaimer: this plan is indicative only. Offers, costs, and returns can change and should be checked at the source before making any decision.",
    "disclaimer.chat": "Disclaimer: personalized answers are informational and educational only and do not replace financial, tax, legal, or investment advice.",
    "offers.safe": "Savings and government securities",
    "offers.funds": "Funds and ETFs",
    "offers.stocks": "Stocks",
    "offers.loans": "Financing for the gap",
    "offers.brokers": "Brokers for ETFs and stocks",
    "offers.safeEmpty": "For this timeline, no safer option looks more suitable right now than classic saving.",
    "offers.fundsEmpty": "For this goal, adding riskier funds or ETFs does not make much sense right now.",
    "offers.stocksEmpty": "Individual stocks only appear for a more aggressive profile and a longer horizon.",
    "offers.brokersEmpty": "Broker options appear here when the plan includes ETFs, funds, or stocks that need execution through a trading platform.",
    "offers.loansEmpty": "No outside financing is needed for this goal.",
    "offers.loansNotRealistic": "There is no loan offer yet that fits this gap realistically within your budget.",
    "offers.source": "Source: {source}",
    "offers.perYear": "{value}% per year",
    "offers.apr": "APR {value}%",
    "offers.monthlyPayment": "payment ~{value} {currency}/month",
    "offers.paymentCap": "profile cap ~{value} {currency}/month",
    "offers.affordableAmount": "realistic financing ~{value} {currency}",
    "offers.remainingGap": "still uncovered ~{value} {currency}",
    "offers.fullCoverage": "can cover the full reviewed amount",
    "offers.partialCoverage": "covers only part of the reviewed amount",
    "offers.quote": "quote ~{value} {currency}",
    "offers.minimumFrom": "minimum {value} {currency}",
    "offers.costAnnual": "annual cost ~{value}%",
    "offers.costTransaction": "transaction cost ~{value}%",
    "offers.costFx": "FX ~{value}%",
    "offers.costSubscription": "subscription {value}%",
    "offers.costRedemption": "redemption {value}%",
    "offers.costCustody": "custody {value}%",
    "offers.costLabel": "Costs",
    "chat.kicker": "Personalized chat",
    "chat.title": "Ask directly",
    "chat.hint": "The answers use your profile and your plan.",
    "chat.placeholder": "Ex: I want a 9000 RON vacation in 6 months. What should I do?",
    "chat.send": "Send",
    "chat.empty": "Hi! Once you complete your profile, I will answer based on your financial situation.",
    "chat.answering": "The coach is replying...",
    "chat.fallback": "Response generated locally.",
    "chat.ai": "Response generated with AI.",
    "chat.error": "I could not answer right now. Please try again.",
    "pwa.install": "Install app",
    "pwa.installReady": "You can install the app on your phone or desktop directly from the browser.",
    "pwa.installing": "Preparing installation...",
    "pwa.installed": "The app has been installed.",
    "pwa.installIos": "On iPhone or iPad, use Share and then Add to Home Screen.",
    "pwa.online": "Online",
    "pwa.offline": "Offline",
    "pwa.offlineTitle": "Offline mode is active",
    "pwa.offlineBody": "You are viewing the last saved state on this device. Chat and live offers return when you are back online.",
    "pwa.offlineCached": "You are offline. Showing the last saved state from this device.",
    "pwa.backOnline": "Connection is back. Live data can refresh again.",
    "common.user": "user",
    "common.error": "Something went wrong.",
    "common.years.one": "year",
    "common.years.other": "years",
    "common.months": "months",
    "common.none": "-",
  },
};

const state = {
  mode: "login",
  locale: localStorage.getItem("aimoneycoach_locale") || "ro",
  token: localStorage.getItem("aimoneycoach_token") || "",
  userEmail: localStorage.getItem("aimoneycoach_email") || "",
  userName: localStorage.getItem("aimoneycoach_name") || "",
  overview: null,
  chatHistory: [],
  goalPayload: null,
  goalPlan: null,
  goalSimulationTimer: null,
  deferredInstallPrompt: null,
  isOnline: window.navigator.onLine,
};

const authPanel = document.getElementById("authPanel");
const appPanel = document.getElementById("appPanel");
const authForm = document.getElementById("authForm");
const profileForm = document.getElementById("profileForm");
const goalForm = document.getElementById("goalForm");
const chatForm = document.getElementById("chatForm");
const authMessage = document.getElementById("authMessage");
const profileMessage = document.getElementById("profileMessage");
const goalMessage = document.getElementById("goalMessage");
const chatMessage = document.getElementById("chatMessage");
const fullNameField = document.getElementById("fullNameField");
const authSubmitBtn = document.getElementById("authSubmitBtn");
const userGreeting = document.getElementById("userGreeting");
const aiStateBadge = document.getElementById("aiStateBadge");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const clearDataBtn = document.getElementById("clearDataBtn");
const emergencyPreviewTitle = document.getElementById("emergencyPreviewTitle");
const emergencyPreviewMeta = document.getElementById("emergencyPreviewMeta");
const goalScoreRing = document.getElementById("goalScoreRing");
const goalScoreValue = document.getElementById("goalScoreValue");
const goalScoreLabel = document.getElementById("goalScoreLabel");
const goalScoreSummary = document.getElementById("goalScoreSummary");
const goalPieChart = document.getElementById("goalPieChart");
const goalPieLegend = document.getElementById("goalPieLegend");
const goalSimulatorRange = document.getElementById("goalSimulatorRange");
const goalSimulatorValue = document.getElementById("goalSimulatorValue");
const goalSimulatorHint = document.getElementById("goalSimulatorHint");
const goalVariants = document.getElementById("goalVariants");
const connectionBadge = document.getElementById("connectionBadge");
const installAppBtn = document.getElementById("installAppBtn");
const pwaHelperText = document.getElementById("pwaHelperText");
const offlineBanner = document.getElementById("offlineBanner");
const CACHE_KEYS = ["overview", "goal_payload", "goal_plan", "chat_history"];

function t(key, vars = {}) {
  const localeSet = translations[state.locale] || translations.ro;
  let template = localeSet[key] ?? translations.ro[key] ?? key;
  for (const [name, value] of Object.entries(vars)) {
    template = template.replaceAll(`{${name}}`, String(value));
  }
  return template;
}

function scopedCacheKey(name, email = state.userEmail) {
  if (!email) {
    return "";
  }
  return `aimoneycoach_cache_${email}_${name}`;
}

function readCachedValue(name, email = state.userEmail) {
  const key = scopedCacheKey(name, email);
  if (!key) {
    return null;
  }

  try {
    const rawValue = localStorage.getItem(key);
    return rawValue ? JSON.parse(rawValue) : null;
  } catch {
    return null;
  }
}

function saveCachedValue(name, value, email = state.userEmail) {
  const key = scopedCacheKey(name, email);
  if (!key) {
    return;
  }

  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {}
}

function clearCachedView(email = state.userEmail) {
  if (!email) {
    return;
  }

  for (const key of CACHE_KEYS) {
    localStorage.removeItem(scopedCacheKey(key, email));
  }
}

function isStandaloneMode() {
  return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

function isIosDevice() {
  return /iphone|ipad|ipod/i.test(window.navigator.userAgent);
}

function setPwaHelperText(message = "") {
  pwaHelperText.textContent = message;
  pwaHelperText.classList.toggle("hidden", !message);
}

function syncInstallPrompt() {
  if (isStandaloneMode()) {
    installAppBtn.classList.add("hidden");
    setPwaHelperText("");
    return;
  }

  if (state.deferredInstallPrompt) {
    installAppBtn.classList.remove("hidden");
    setPwaHelperText(t("pwa.installReady"));
    return;
  }

  installAppBtn.classList.add("hidden");
  setPwaHelperText(isIosDevice() ? t("pwa.installIos") : "");
}

function setConnectionState(isOnline, showRecoveryMessage = false) {
  state.isOnline = Boolean(isOnline);
  connectionBadge.textContent = t(state.isOnline ? "pwa.online" : "pwa.offline");
  connectionBadge.classList.toggle("offline", !state.isOnline);
  offlineBanner.classList.toggle("hidden", state.isOnline);

  if (showRecoveryMessage && state.isOnline && state.token) {
    setStatus(chatMessage, t("pwa.backOnline"));
  }
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }

  try {
    await navigator.serviceWorker.register("/service-worker.js");
  } catch (error) {
    console.warn("Service worker registration failed", error);
  }
}

async function promptInstallApp() {
  if (!state.deferredInstallPrompt) {
    syncInstallPrompt();
    return;
  }

  setPwaHelperText(t("pwa.installing"));
  state.deferredInstallPrompt.prompt();
  const { outcome } = await state.deferredInstallPrompt.userChoice;
  state.deferredInstallPrompt = null;

  if (outcome === "accepted") {
    setPwaHelperText(t("pwa.installed"));
  }

  syncInstallPrompt();
}

function applyGoalPayloadToForm(payload) {
  if (!payload) {
    return;
  }

  goalForm.elements.goal_name.value = payload.goal_name || "";
  goalForm.elements.target_amount.value = payload.target_amount || "";
  goalForm.elements.target_currency.value = payload.target_currency || "RON";
  goalForm.elements.target_months.value = payload.target_months || "";
  goalForm.elements.allow_credit_gap.checked = payload.allow_credit_gap !== false;
}

function hydrateCachedGoalPayload() {
  if (state.goalPayload) {
    applyGoalPayloadToForm(state.goalPayload);
    return;
  }

  const cachedPayload = readCachedValue("goal_payload");
  if (!cachedPayload) {
    return;
  }

  state.goalPayload = cachedPayload;
  applyGoalPayloadToForm(cachedPayload);
}

function restoreCachedView() {
  const cachedOverview = readCachedValue("overview");
  const cachedHistory = readCachedValue("chat_history");
  const cachedPayload = readCachedValue("goal_payload");
  const cachedPlan = readCachedValue("goal_plan");
  const hasHistory = Array.isArray(cachedHistory) && cachedHistory.length > 0;

  if (!cachedOverview && !cachedPayload && !cachedPlan && !hasHistory) {
    return false;
  }

  resetOverviewOutputs();

  if (cachedOverview) {
    renderOverview(cachedOverview);
  }

  if (cachedPayload) {
    state.goalPayload = cachedPayload;
    applyGoalPayloadToForm(cachedPayload);
  }

  if (cachedPlan) {
    renderGoalPlan(cachedPlan);
  }

  if (Array.isArray(cachedHistory)) {
    renderHistory(cachedHistory);
  } else {
    renderHistory([]);
  }

  setStatus(chatMessage, t("pwa.offlineCached"));
  return true;
}

function applyTranslations() {
  document.documentElement.lang = state.locale;

  for (const element of document.querySelectorAll("[data-i18n]")) {
    element.textContent = t(element.dataset.i18n);
  }

  for (const element of document.querySelectorAll("[data-i18n-placeholder]")) {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  }

  authSubmitBtn.textContent = state.mode === "login" ? t("auth.submitLogin") : t("auth.submitRegister");
  updateEmergencyPreview();
  setConnectionState(state.isOnline);
  syncInstallPrompt();
  document.documentElement.setAttribute("data-i18n-ready", "true");
}

function syncLocaleButtons() {
  for (const button of document.querySelectorAll(".lang-btn")) {
    button.classList.toggle("active", button.dataset.locale === state.locale);
  }
}

function setLocale(locale) {
  state.locale = locale === "en" ? "en" : "ro";
  localStorage.setItem("aimoneycoach_locale", state.locale);
  syncLocaleButtons();
  applyTranslations();
  if (!state.token) {
    renderHistory([]);
    resetOverviewOutputs();
    return;
  }

  refreshLocalizedData().catch(() => {});
}

function setMode(mode) {
  state.mode = mode;
  for (const button of document.querySelectorAll(".switch-btn")) {
    button.classList.toggle("active", button.dataset.mode === mode);
  }
  fullNameField.classList.toggle("hidden", mode !== "register");
  authSubmitBtn.textContent = mode === "login" ? t("auth.submitLogin") : t("auth.submitRegister");
  authMessage.textContent = "";
}

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.style.color = isError ? "#9f2f2f" : "";
}

function saveSession(token, email, fullName) {
  state.token = token;
  state.userEmail = email || "";
  state.userName = fullName || "";
  localStorage.setItem("aimoneycoach_token", token);
  localStorage.setItem("aimoneycoach_email", state.userEmail);
  localStorage.setItem("aimoneycoach_name", state.userName);
}

function clearSession() {
  const currentEmail = state.userEmail;
  clearCachedView(currentEmail);
  state.token = "";
  state.userEmail = "";
  state.userName = "";
  state.overview = null;
  state.chatHistory = [];
  state.goalPayload = null;
  state.goalPlan = null;
  localStorage.removeItem("aimoneycoach_token");
  localStorage.removeItem("aimoneycoach_email");
  localStorage.removeItem("aimoneycoach_name");
}

function showAuth() {
  authPanel.classList.remove("hidden");
  appPanel.classList.add("hidden");
}

function showApp() {
  authPanel.classList.add("hidden");
  appPanel.classList.remove("hidden");
  userGreeting.textContent = state.userName || state.userEmail || t("common.user");
}

function parseGoals(rawValue) {
  return rawValue
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return t("common.none");
  }
  return `${Math.round(Number(value))} RON`;
}

function formatTerm(months) {
  if (!months && months !== 0) {
    return "";
  }
  if (months === 0) {
    return `0 ${t("common.months")}`;
  }
  if (months % 12 === 0 && months >= 12) {
    const years = months / 12;
    const label = years === 1 ? t("common.years.one") : t("common.years.other");
    return `${years} ${label}`;
  }
  return `${months} ${t("common.months")}`;
}

function computeEmergencyTargetMonths() {
  const income = Number(profileForm.elements.monthly_income.value || 0);
  const expenses = Number(profileForm.elements.monthly_expenses.value || 0);
  const debts = Number(profileForm.elements.debts.value || 0);
  const riskProfile = profileForm.elements.risk_profile.value || "moderate";
  const savingsCapacity = income - expenses;
  const savingsRate = income > 0 ? savingsCapacity / income : 0;
  const debtRatio = income > 0 ? debts / (income * 12) : 0;

  if (riskProfile === "conservative" || savingsCapacity <= 0 || debtRatio >= 0.4) {
    return 9;
  }
  if (riskProfile === "aggressive" && savingsRate >= 0.2 && debtRatio <= 0.2) {
    return 3;
  }
  return 6;
}

function updateEmergencyPreview() {
  if (!emergencyPreviewTitle || !emergencyPreviewMeta) {
    return;
  }

  const expenses = Number(profileForm.elements.monthly_expenses.value || 0);
  const emergencyFund = Number(profileForm.elements.emergency_fund.value || 0);

  if (expenses <= 0) {
    emergencyPreviewTitle.textContent = t("profile.emergencyPreviewDefault");
    emergencyPreviewMeta.textContent = "";
    return;
  }

  const currentMonths = emergencyFund / expenses;
  const targetMonths = computeEmergencyTargetMonths();
  const targetAmount = targetMonths * expenses;
  const shortfall = Math.max(0, targetAmount - emergencyFund);

  emergencyPreviewTitle.textContent = t("profile.emergencyPreviewCurrent", {
    current: currentMonths.toFixed(1),
  });
  emergencyPreviewMeta.textContent = [
    t("profile.emergencyPreviewTarget", {
      target: targetMonths,
      amount: Math.round(targetAmount),
    }),
    shortfall > 0
      ? t("profile.emergencyPreviewShortfall", { amount: Math.round(shortfall) })
      : t("profile.emergencyPreviewReady"),
  ].join(" ");
}

function formatOfferMeta(offer) {
  const parts = [];

  if (offer.annual_rate_percent !== null && offer.annual_rate_percent !== undefined) {
    parts.push(t("offers.perYear", { value: Number(offer.annual_rate_percent).toFixed(2) }));
  }
  if (offer.dae_percent !== null && offer.dae_percent !== undefined) {
    parts.push(t("offers.apr", { value: Number(offer.dae_percent).toFixed(2) }));
  }
  if (offer.term_months) {
    parts.push(formatTerm(offer.term_months));
  }
  if (offer.minimum_amount) {
    parts.push(
      t("offers.minimumFrom", {
        value: Math.round(offer.minimum_amount),
        currency: offer.currency,
      })
    );
  }
  if (offer.indicative_monthly_payment) {
    parts.push(
      t("offers.monthlyPayment", {
        value: Math.round(offer.affordable_monthly_payment || offer.indicative_monthly_payment),
        currency: offer.currency,
      })
    );
  }
  if (offer.monthly_payment_cap) {
    parts.push(
      t("offers.paymentCap", {
        value: Math.round(offer.monthly_payment_cap),
        currency: offer.currency,
      })
    );
  }
  if (offer.affordable_amount) {
    parts.push(
      t("offers.affordableAmount", {
        value: Math.round(offer.affordable_amount),
        currency: offer.currency,
      })
    );
  }
  if (offer.covers_full_request === true) {
    parts.push(t("offers.fullCoverage"));
  } else if (offer.covers_full_request === false) {
    parts.push(t("offers.partialCoverage"));
  }
  if (offer.uncovered_gap_after_offer) {
    parts.push(
      t("offers.remainingGap", {
        value: Math.round(offer.uncovered_gap_after_offer),
        currency: offer.currency,
      })
    );
  }
  if (offer.indicative_price) {
    parts.push(
      t("offers.quote", {
        value: offer.indicative_price,
        currency: offer.currency,
      })
    );
  }

  return parts.join(" | ");
}

function formatOfferCosts(offer) {
  const parts = [];

  if (offer.annual_cost_percent !== null && offer.annual_cost_percent !== undefined) {
    parts.push(t("offers.costAnnual", { value: Number(offer.annual_cost_percent).toFixed(2) }));
  }
  if (offer.transaction_cost_percent !== null && offer.transaction_cost_percent !== undefined) {
    parts.push(t("offers.costTransaction", { value: Number(offer.transaction_cost_percent).toFixed(2) }));
  }
  if (offer.fx_conversion_cost_percent !== null && offer.fx_conversion_cost_percent !== undefined) {
    parts.push(t("offers.costFx", { value: Number(offer.fx_conversion_cost_percent).toFixed(2) }));
  }
  if (offer.subscription_fee_percent !== null && offer.subscription_fee_percent !== undefined) {
    parts.push(t("offers.costSubscription", { value: Number(offer.subscription_fee_percent).toFixed(2) }));
  }
  if (offer.redemption_fee_percent !== null && offer.redemption_fee_percent !== undefined) {
    parts.push(t("offers.costRedemption", { value: Number(offer.redemption_fee_percent).toFixed(2) }));
  }
  if (offer.custody_fee_percent !== null && offer.custody_fee_percent !== undefined) {
    parts.push(t("offers.costCustody", { value: Number(offer.custody_fee_percent).toFixed(2) }));
  }
  if (offer.cost_summary) {
    parts.push(offer.cost_summary);
  }

  return parts.join(" | ");
}

function renderOfferList(containerId, offers, emptyMessage) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";

  if (!offers.length) {
    const empty = document.createElement("p");
    empty.className = "offer-empty";
    empty.textContent = emptyMessage;
    container.appendChild(empty);
    return;
  }

  for (const offer of offers) {
    const card = document.createElement("article");
    card.className = "offer-item";

    const title = document.createElement("h6");
    title.textContent = offer.product_name;

    const provider = document.createElement("p");
    provider.className = "offer-provider";
    provider.textContent = offer.bank_rank ? `#${offer.bank_rank} ${offer.provider}` : offer.provider;

    const meta = document.createElement("p");
    meta.className = "offer-meta";
    meta.textContent = formatOfferMeta(offer) || offer.suitability;

    const note = document.createElement("p");
    note.className = "offer-note";
    note.textContent = offer.note;

    const costs = document.createElement("p");
    costs.className = "offer-costs";
    costs.textContent = formatOfferCosts(offer);

    const source = document.createElement("a");
    source.className = "offer-source";
    source.href = offer.source_url;
    source.target = "_blank";
    source.rel = "noreferrer";
    source.textContent = t("offers.source", { source: offer.source_name });

    if (!costs.textContent) {
      costs.remove();
    }

    card.append(title, provider, meta, costs, note, source);
    container.appendChild(card);
  }
}

function renderGoalScore(plan) {
  const score = plan.achievement?.score ?? 0;
  const color = plan.achievement?.color ?? "#2f7a78";
  const degrees = Math.round((score / 100) * 360);
  goalScoreRing.style.background = `conic-gradient(${color} 0deg ${degrees}deg, rgba(31, 106, 90, 0.12) ${degrees}deg 360deg)`;
  goalScoreValue.textContent = score ? `${score}` : t("common.none");
  goalScoreLabel.textContent = plan.achievement?.label ?? t("common.none");
  goalScoreSummary.textContent = plan.achievement?.summary ?? t("goal.scoreDefault");
}

function renderGoalPie(plan) {
  goalPieLegend.innerHTML = "";
  const slices = plan.objective_pie || [];

  if (!slices.length) {
    goalPieChart.style.background = "conic-gradient(rgba(31, 106, 90, 0.12) 0deg 360deg)";
    const empty = document.createElement("p");
    empty.className = "offer-empty";
    empty.textContent = t("goal.pieEmpty");
    goalPieLegend.appendChild(empty);
    return;
  }

  const total = slices.reduce((sum, item) => sum + Number(item.value || 0), 0);
  let currentDeg = 0;
  const gradientParts = [];

  for (const slice of slices) {
    const portion = total > 0 ? (Number(slice.value) / total) * 360 : 0;
    const nextDeg = currentDeg + portion;
    gradientParts.push(`${slice.color} ${currentDeg}deg ${nextDeg}deg`);
    currentDeg = nextDeg;

    const item = document.createElement("div");
    item.className = "pie-legend-item";

    const dot = document.createElement("span");
    dot.className = "pie-dot";
    dot.style.background = slice.color;

    const copy = document.createElement("div");
    copy.className = "pie-legend-copy";

    const title = document.createElement("strong");
    title.textContent = slice.label;

    const value = document.createElement("span");
    value.textContent = `${formatCurrency(slice.value)} (${Math.round((Number(slice.value) / total) * 100)}%)`;

    copy.append(title, value);
    item.append(dot, copy);
    goalPieLegend.appendChild(item);
  }

  goalPieChart.style.background = `conic-gradient(${gradientParts.join(", ")})`;
}

function renderGoalVariants(plan) {
  goalVariants.innerHTML = "";
  const variants = plan.plan_variants || [];
  if (!variants.length) {
    const empty = document.createElement("p");
    empty.className = "offer-empty";
    empty.textContent = t("goal.scoreDefault");
    goalVariants.appendChild(empty);
    return;
  }

  for (const variant of variants) {
    const card = document.createElement("article");
    card.className = `variant-card${variant.is_recommended ? " recommended" : ""}`;

    const titleRow = document.createElement("div");
    titleRow.className = "variant-title-row";

    const titleWrap = document.createElement("div");
    const title = document.createElement("h6");
    title.textContent = variant.title;
    const subtitle = document.createElement("p");
    subtitle.textContent = variant.subtitle;
    titleWrap.append(title, subtitle);

    const badge = document.createElement("span");
    badge.className = "variant-badge";
    badge.textContent = variant.is_recommended ? t("goal.variantRecommended") : variant.achievement.label;
    badge.style.background = `${variant.color}1A`;
    badge.style.color = variant.color;

    titleRow.append(titleWrap, badge);

    const kpis = document.createElement("div");
    kpis.className = "variant-kpi";
    const kpiItems = [
      [t("goal.variantScore"), `${variant.achievement.score}/100`],
      [t("goal.variantMonthly"), formatCurrency(variant.monthly_contribution)],
      [t("goal.variantProjected"), formatCurrency(variant.projected_total)],
      [t("goal.variantTimeline"), formatTerm(variant.estimated_completion_months)],
    ];

    for (const [label, value] of kpiItems) {
      const box = document.createElement("div");
      const kpiLabel = document.createElement("p");
      kpiLabel.textContent = label;
      const kpiValue = document.createElement("strong");
      kpiValue.textContent = value;
      box.append(kpiLabel, kpiValue);
      kpis.appendChild(box);
    }

    const chipRow = document.createElement("div");
    chipRow.className = "variant-chip-row";
    const chipValues = [
      `${t("goal.variantEmergency")}: ${formatTerm(variant.emergency_months_kept)}`,
      `${t("goal.variantInstrument")}: ${variant.primary_instrument}`,
      variant.funding_gap > 0
        ? `${t("goal.variantGap")}: ${formatCurrency(variant.funding_gap)}`
        : t("goal.variantOnTrack"),
      variant.uses_credit ? t("goal.variantUsesCredit") : t("goal.variantNoCredit"),
    ];

    for (const chipText of chipValues) {
      const chip = document.createElement("span");
      chip.className = "variant-chip";
      chip.textContent = chipText;
      chipRow.appendChild(chip);
    }

    const summaryWrap = document.createElement("div");
    summaryWrap.className = "variant-summary";
    const summary = document.createElement("p");
    summary.textContent = variant.summary;
    summaryWrap.appendChild(summary);

    card.append(titleRow, kpis, chipRow, summaryWrap);
    goalVariants.appendChild(card);
  }
}

function configureSimulator(plan) {
  goalSimulatorRange.disabled = false;
  goalSimulatorRange.min = "0";
  goalSimulatorRange.max = String(Math.round(plan.simulator_max_extra_monthly_savings || 0));
  goalSimulatorRange.step = String(Math.round(plan.simulator_step || 100));
  goalSimulatorRange.value = String(Math.round(plan.simulator_extra_monthly_savings || 0));
  goalSimulatorValue.textContent = t("goal.simulatorValue", {
    amount: Math.round(plan.simulator_extra_monthly_savings || 0),
  });
  goalSimulatorHint.textContent = plan.achievement?.summary || t("goal.simulatorHintActive");
}

function resetSimulator() {
  goalSimulatorRange.disabled = true;
  goalSimulatorRange.min = "0";
  goalSimulatorRange.max = "0";
  goalSimulatorRange.step = "100";
  goalSimulatorRange.value = "0";
  goalSimulatorValue.textContent = t("goal.simulatorValue", { amount: 0 });
  goalSimulatorHint.textContent = t("goal.simulatorHint");
}

function resetGoalOutputs() {
  state.goalPlan = null;
  document.getElementById("goalSummary").textContent = t("overview.defaultGoalSummary");
  document.getElementById("goalInsights").innerHTML = "";
  document.getElementById("goalNextActions").innerHTML = "";
  document.getElementById("loanMarketSummary").textContent = "";
  document.getElementById("loanMarketBanks").textContent = "";
  document.getElementById("loanMarketCreditRule").textContent = "";
  document.getElementById("loanMarketBox").classList.add("hidden");
  document.getElementById("goalSafeOffers").innerHTML = "";
  document.getElementById("goalFundOffers").innerHTML = "";
  document.getElementById("goalStockOffers").innerHTML = "";
  document.getElementById("goalBrokerOffers").innerHTML = "";
  document.getElementById("goalLoanOffers").innerHTML = "";
  goalVariants.innerHTML = "";
  renderGoalScore({ achievement: null });
  renderGoalPie({ objective_pie: [] });
  resetSimulator();
}

function resetOverviewOutputs() {
  state.overview = null;
  state.chatHistory = [];
  document.getElementById("healthScoreValue").textContent = "-";
  document.getElementById("riskScoreValue").textContent = "-";
  document.getElementById("savingsCapacityValue").textContent = "-";
  document.getElementById("emergencyFundValue").textContent = "-";
  document.getElementById("snapshotSummary").textContent = t("overview.defaultSnapshot");
  document.getElementById("planSummary").textContent = t("overview.defaultPlan");
  document.getElementById("nextStepText").textContent = t("overview.defaultNextStep");
  profileForm.reset();
  updateEmergencyPreview();
  resetGoalOutputs();
}

function renderOverview(overview) {
  state.overview = overview;
  saveCachedValue("overview", overview);
  const displayName = overview.full_name || overview.email || state.userEmail;
  if (overview.full_name) {
    state.userName = overview.full_name;
    localStorage.setItem("aimoneycoach_name", overview.full_name);
  }
  userGreeting.textContent = displayName || t("common.user");
  aiStateBadge.textContent = overview.ai_enabled ? t("dashboard.aiEnabled") : t("dashboard.aiFallback");

  const snapshot = overview.financial_snapshot;
  const recommendation = overview.latest_recommendation;

  document.getElementById("healthScoreValue").textContent = snapshot ? `${snapshot.financial_health_score}/100` : "-";
  document.getElementById("riskScoreValue").textContent = snapshot ? `${snapshot.risk_score}/100` : "-";
  document.getElementById("savingsCapacityValue").textContent = snapshot ? formatCurrency(snapshot.monthly_savings_capacity) : "-";
  document.getElementById("emergencyFundValue").textContent = snapshot
    ? `${snapshot.emergency_fund.current_months} / ${snapshot.emergency_fund.target_months} ${t("common.months")}`
    : "-";
  document.getElementById("snapshotSummary").textContent = snapshot
    ? snapshot.summary
    : t("overview.defaultSnapshot");
  document.getElementById("planSummary").textContent = recommendation
    ? recommendation.summary
    : t("overview.defaultPlan");
  document.getElementById("nextStepText").textContent = overview.next_step || t("overview.defaultNextStep");

  if (snapshot) {
    profileForm.elements.monthly_income.value = snapshot.monthly_income;
    profileForm.elements.monthly_expenses.value = snapshot.monthly_expenses;
    profileForm.elements.age.value = snapshot.age ?? "";
    profileForm.elements.credit_gender.value = snapshot.credit_gender || "male";
    profileForm.elements.emergency_fund.value = snapshot.emergency_fund.current_amount;
    profileForm.elements.savings.value = snapshot.savings;
    profileForm.elements.debts.value = snapshot.debts;
    profileForm.elements.risk_profile.value = snapshot.risk_profile;
    profileForm.elements.financial_goals.value = (snapshot.financial_goals || []).join(", ");
    updateEmergencyPreview();
  } else {
    profileForm.reset();
    updateEmergencyPreview();
  }
}

function renderGoalPlan(plan) {
  state.goalPlan = plan;
  saveCachedValue("goal_plan", plan);
  applyGoalPayloadToForm(state.goalPayload);

  const summary = `${plan.strategy_summary} ${
    plan.feasible_without_credit
      ? t("goal.feasible")
      : t("goal.gap", { amount: Math.round(plan.funding_gap) })
  }`;
  document.getElementById("goalSummary").textContent = summary;

  renderGoalScore(plan);
  renderGoalPie(plan);
  renderGoalVariants(plan);
  configureSimulator(plan);

  const insights = document.getElementById("goalInsights");
  insights.innerHTML = "";

  const chips = [
    t("goal.chipSavings", { amount: Math.round(plan.effective_monthly_contribution || plan.monthly_savings_capacity) }),
    t("goal.chipAvailable", { amount: Math.round(plan.available_now_for_goal) }),
    t("goal.chipProjected", { amount: Math.round(plan.projected_savings_by_deadline) }),
    t("goal.chipEmergency", { amount: Math.round(plan.emergency_fund_to_keep) }),
  ];

  if (plan.credit_age_rule_note) {
    chips.push(plan.credit_age_rule_note);
  }
  if (plan.credit_affordability_note) {
    chips.push(plan.credit_affordability_note);
  }

  if (plan.safe_saving_offers.length) {
    const bestSafe = plan.safe_saving_offers[0];
    chips.push(
      t("goal.chipSafe", {
        provider: bestSafe.provider,
        product: bestSafe.product_name,
        rate: bestSafe.annual_rate_percent ? bestSafe.annual_rate_percent.toFixed(2) : "-",
      })
    );
  }

  if (plan.loan_options.length && !plan.feasible_without_credit) {
    const bestLoan = plan.loan_options[0];
    chips.push(
      t("goal.chipLoan", {
        provider: bestLoan.provider,
        product: bestLoan.product_name,
        rate: bestLoan.dae_percent ? bestLoan.dae_percent.toFixed(2) : "-",
        payment: Math.round(bestLoan.affordable_monthly_payment || bestLoan.indicative_monthly_payment || 0),
      })
    );
  }

  if (plan.investment_options.length) {
    const firstInvestment = plan.investment_options[0];
    chips.push(
      t("goal.chipInvestment", {
        product: firstInvestment.product_name,
        price: firstInvestment.indicative_price ?? "-",
        currency: firstInvestment.currency,
      })
    );
  }

  for (const chipText of chips) {
    const item = document.createElement("div");
    item.className = "goal-chip";
    item.textContent = chipText;
    insights.appendChild(item);
  }

  const nextActions = document.getElementById("goalNextActions");
  nextActions.innerHTML = "";
  for (const action of plan.next_actions) {
    const item = document.createElement("div");
    item.className = "goal-action-item";
    item.textContent = action;
    nextActions.appendChild(item);
  }

  const loanMarketBox = document.getElementById("loanMarketBox");
  const loanMarketSummary = document.getElementById("loanMarketSummary");
  const loanMarketBanks = document.getElementById("loanMarketBanks");
  const loanMarketCreditRule = document.getElementById("loanMarketCreditRule");
  if (plan.loan_market_scope?.length) {
    loanMarketBox.classList.remove("hidden");
    loanMarketSummary.textContent = t("goal.marketSummary", {
      scopeCount: plan.loan_market_scope.length,
      family: (plan.loan_product_family_label || t("goal.marketFallbackFamily")).toLowerCase(),
      offerCount: plan.loan_options?.length || 0,
    });
    loanMarketBanks.textContent = t("goal.marketBanks", {
      banks: plan.loan_market_scope.join(", "),
    });
    loanMarketCreditRule.textContent = [plan.credit_affordability_note, plan.credit_age_rule_note]
      .filter(Boolean)
      .join(" ");
  } else {
    loanMarketSummary.textContent = "";
    loanMarketBanks.textContent = "";
    loanMarketCreditRule.textContent = "";
    loanMarketBox.classList.add("hidden");
  }

  const fundOffers = plan.investment_options.filter((offer) => offer.category !== "stock");
  const stockOffers = plan.investment_options.filter((offer) => offer.category === "stock");

  renderOfferList("goalSafeOffers", plan.safe_saving_offers, t("offers.safeEmpty"));
  renderOfferList("goalFundOffers", fundOffers, t("offers.fundsEmpty"));
  renderOfferList("goalStockOffers", stockOffers, t("offers.stocksEmpty"));
  renderOfferList("goalBrokerOffers", plan.broker_options || [], t("offers.brokersEmpty"));
  renderOfferList(
    "goalLoanOffers",
    plan.loan_options,
    plan.feasible_without_credit ? t("offers.loansEmpty") : t("offers.loansNotRealistic")
  );
}

function addChatBubble(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  bubble.textContent = text;
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function renderHistory(items) {
  state.chatHistory = Array.isArray(items) ? items : [];
  saveCachedValue("chat_history", state.chatHistory);
  chatMessages.innerHTML = "";
  if (!items.length) {
    addChatBubble("assistant", t("chat.empty"));
    return;
  }

  const history = [...items].reverse();
  for (const item of history) {
    addChatBubble("user", item.message);
    addChatBubble("assistant", item.response);
  }
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Accept-Language", state.locale);

  if (state.token) {
    headers.set("Authorization", `Bearer ${state.token}`);
  }
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(path, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const detail = typeof data === "object" && data?.detail ? data.detail : t("common.error");
    throw new Error(detail);
  }

  return data;
}

async function loadOverview() {
  const overview = await apiFetch("/coach/overview");
  renderOverview(overview);
}

async function loadHistory() {
  const history = await apiFetch("/chat/history?limit=12");
  renderHistory(history);
}

async function runGoalPlan(payload) {
  state.goalPayload = payload;
  saveCachedValue("goal_payload", payload);
  applyGoalPayloadToForm(payload);
  const plan = await apiFetch("/coach/goal-plan", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  renderGoalPlan(plan);
  return plan;
}

async function rerunGoalPlan() {
  if (!state.goalPayload) {
    resetGoalOutputs();
    return;
  }

  try {
    await runGoalPlan(state.goalPayload);
  } catch {
    resetGoalOutputs();
  }
}

async function refreshLocalizedData() {
  await loadOverview();
  await loadHistory();
  await rerunGoalPlan();
}

async function bootAuthenticatedView() {
  showApp();
  hydrateCachedGoalPayload();
  if (!state.isOnline && restoreCachedView()) {
    return;
  }
  await loadOverview();
  await loadHistory();
  hydrateCachedGoalPayload();
  await rerunGoalPlan();
}

function queueGoalSimulation() {
  if (!state.goalPayload) {
    return;
  }
  const sliderValue = Number(goalSimulatorRange.value || 0);
  state.goalPayload.extra_monthly_savings = sliderValue;
  goalSimulatorValue.textContent = t("goal.simulatorValue", { amount: Math.round(sliderValue) });
  goalSimulatorHint.textContent = t("goal.simulatorHintActive");

  if (state.goalSimulationTimer) {
    clearTimeout(state.goalSimulationTimer);
  }

  state.goalSimulationTimer = setTimeout(async () => {
    try {
      const plan = await runGoalPlan(state.goalPayload);
      setStatus(goalMessage, t("goal.generated"));
      goalSimulatorValue.textContent = t("goal.simulatorValue", {
        amount: Math.round(plan.simulator_extra_monthly_savings || 0),
      });
    } catch (error) {
      setStatus(goalMessage, error.message, true);
    }
  }, 220);
}

document.querySelectorAll(".switch-btn").forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

document.querySelectorAll(".lang-btn").forEach((button) => {
  button.addEventListener("click", () => setLocale(button.dataset.locale));
});

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  state.deferredInstallPrompt = event;
  syncInstallPrompt();
});

window.addEventListener("appinstalled", () => {
  state.deferredInstallPrompt = null;
  installAppBtn.classList.add("hidden");
  setPwaHelperText(t("pwa.installed"));
});

window.addEventListener("online", async () => {
  setConnectionState(true, true);
  if (!state.token) {
    return;
  }

  try {
    await refreshLocalizedData();
  } catch {}
});

window.addEventListener("offline", () => {
  setConnectionState(false);
  if (state.token) {
    restoreCachedView();
  }
});

installAppBtn.addEventListener("click", () => {
  promptInstallApp().catch(() => {
    syncInstallPrompt();
  });
});

goalSimulatorRange.addEventListener("input", queueGoalSimulation);
profileForm.addEventListener("input", updateEmergencyPreview);
profileForm.addEventListener("change", updateEmergencyPreview);

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(authMessage, t("auth.processing"));

  const email = document.getElementById("emailInput").value.trim();
  const password = document.getElementById("passwordInput").value;
  const fullName = document.getElementById("fullNameInput").value.trim();

  try {
    let result;
    if (state.mode === "register") {
      result = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email,
          password,
          full_name: fullName || null,
        }),
      });
      saveSession(result.access_token, result.email, fullName);
    } else {
      result = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      saveSession(result.access_token, result.email, state.userName || fullName);
    }

    setStatus(authMessage, t("auth.success"));
    await bootAuthenticatedView();
  } catch (error) {
    setStatus(authMessage, error.message, true);
  }
});

profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(profileMessage, t("profile.saving"));

  const payload = {
    monthly_income: Number(profileForm.elements.monthly_income.value),
    monthly_expenses: Number(profileForm.elements.monthly_expenses.value),
    age: profileForm.elements.age.value ? Number(profileForm.elements.age.value) : null,
    credit_gender: profileForm.elements.credit_gender.value || null,
    emergency_fund: Number(profileForm.elements.emergency_fund.value || 0),
    savings: Number(profileForm.elements.savings.value || 0),
    debts: Number(profileForm.elements.debts.value || 0),
    risk_profile: profileForm.elements.risk_profile.value,
    financial_goals: parseGoals(profileForm.elements.financial_goals.value),
  };

  try {
    const planOverview = await apiFetch("/coach/setup", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderOverview(planOverview);
    setStatus(profileMessage, t("profile.saved"));
  } catch (error) {
    setStatus(profileMessage, error.message, true);
  }
});

goalForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus(goalMessage, t("goal.generating"));

  const payload = {
    goal_name: goalForm.elements.goal_name.value.trim(),
    target_amount: Number(goalForm.elements.target_amount.value),
    target_currency: goalForm.elements.target_currency.value || "RON",
    target_months: Number(goalForm.elements.target_months.value),
    allow_credit_gap: goalForm.elements.allow_credit_gap.checked,
    extra_monthly_savings: Number(goalSimulatorRange.value || 0),
  };

  try {
    state.goalPayload = payload;
    await runGoalPlan(payload);
    setStatus(goalMessage, t("goal.generated"));
  } catch (error) {
    setStatus(goalMessage, error.message, true);
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) {
    return;
  }

  addChatBubble("user", message);
  chatInput.value = "";
  setStatus(chatMessage, t("chat.answering"));

  try {
    const response = await apiFetch("/chat/ask", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    addChatBubble("assistant", response.response);
    state.chatHistory = [
      { message, response: response.response },
      ...state.chatHistory,
    ].slice(0, 12);
    saveCachedValue("chat_history", state.chatHistory);
    setStatus(chatMessage, response.used_ai_fallback ? t("chat.fallback") : t("chat.ai"));
  } catch (error) {
    addChatBubble("assistant", t("chat.error"));
    setStatus(chatMessage, error.message, true);
  }
});

clearDataBtn.addEventListener("click", async () => {
  if (!window.confirm(t("dashboard.clearConfirm"))) {
    return;
  }

  setStatus(profileMessage, t("dashboard.clearing"));
  try {
    await apiFetch("/coach/reset", { method: "DELETE" });
    clearCachedView();
    state.goalPayload = null;
    goalForm.reset();
    renderHistory([]);
    resetOverviewOutputs();
    await loadOverview();
    setStatus(profileMessage, t("dashboard.cleared"));
    setStatus(goalMessage, "");
    setStatus(chatMessage, "");
  } catch (error) {
    setStatus(profileMessage, error.message, true);
  }
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  clearSession();
  renderHistory([]);
  resetOverviewOutputs();
  goalForm.reset();
  showAuth();
  setStatus(authMessage, "");
  setStatus(profileMessage, "");
  setStatus(goalMessage, "");
  setStatus(chatMessage, "");
});

syncLocaleButtons();
applyTranslations();
setMode("login");
registerServiceWorker();

if (state.token) {
  bootAuthenticatedView().catch(() => {
    clearSession();
    showAuth();
    renderHistory([]);
    resetOverviewOutputs();
  });
} else {
  showAuth();
  renderHistory([]);
  resetOverviewOutputs();
}
