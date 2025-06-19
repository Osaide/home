// js/main.js

// Import Neon Cursor - Remains at top level
import { neonCursor } from 'https://unpkg.com/threejs-toys@0.0.8/build/threejs-toys.module.cdn.min.js';

// --- Oggetto Traduzioni --- Remains at top level
const translations = {
    // Navigation
    'nav-home': { it: 'Home', en: 'Home' },
    'nav-mission': { it: 'Missione', en: 'Mission' },
    'nav-vision': { it: 'Visione', en: 'Vision' },
    'nav-services': { it: 'Servizi', en: 'Services' },
    'nav-portfolio': { it: 'Progetti', en: 'Projects' },
    'nav-certifications': { it: 'Competenze', en: 'Skills' },
    'nav-contacts': { it: 'Contatti', en: 'Contacts' },
    'nav-chatbot-demo': { it: 'Chatbot Demo', en: 'Chatbot Demo' },

    // Home Section
    'home-subtitle': { it: "Organizzazione, Science, AI, Dati, Efficienza. Potenziamo le PMI trasformando <span class='highlight'>dati complessi</span> in <span class='highlight'>processi efficienti</span> e decisioni strategiche.", en: "Organization, Science, AI, Data, Efficiency. We empower SMEs by transforming <span class='highlight'>complex data</span> into <span class='highlight'>efficient processes</span> and strategic decisions." },
    'view-work': { it: 'Vedi Progetti', en: 'View Projects' },
    'get-in-touch': { it: 'Contattaci', en: 'Get in Touch' },

    // Mission Section
    'mission-text-1': { it: "Guidare le PMI verso l'<span class=\"highlight\">efficienza operativa</span> e il <span class=\"highlight\">vantaggio competitivo</span> attraverso l'organizzazione intelligente dei processi, potenziata dall'analisi scientifica dei dati e da soluzioni AI mirate.", en: "Guiding SMEs towards <span class=\"highlight\">operational efficiency</span> and <span class=\"highlight\">competitive advantage</span> through intelligent process organization, enhanced by scientific data analysis and targeted AI solutions." },
    'mission-text-2': { it: "Fornire strumenti e metodologie <span class=\"highlight\">su misura</span>, concreti e sostenibili, che trasformino i dati in valore tangibile, rispettando le specificità e i budget di ogni realtà aziendale.", en: "Providing <span class=\"highlight\">tailor-made</span>, concrete, and sustainable tools and methodologies that transform data into tangible value, respecting the specificities and budgets of each business reality." },
    'mission-icon1': { it: 'Affidabilità', en: 'Reliability' },
    'mission-icon2': { it: 'Efficienza', en: 'Efficiency' },
    'mission-icon3': { it: 'Innovazione Pratica', en: 'Practical Innovation' },
    'mission-image-text': { it: 'Dati -> Efficienza -> Crescita', en: 'Data -> Efficiency -> Growth' },

    // Vision Section
    'vision-image-text': { it: "Organizzazioni potenziate dall'intelligenza dei dati", en: "Organizations empowered by data intelligence" },
    'vision-text-1': { it: "Un futuro in cui le PMI competono alla pari grazie a <span class=\"highlight\">organizzazioni agili</span> e <span class=\"highlight\">decisioni data-driven</span>, supportate da sistemi intelligenti che ottimizzano risorse e anticipano le esigenze del mercato.", en: "A future where SMEs compete on equal terms thanks to <span class=\"highlight\">agile organizations</span> and <span class=\"highlight\">data-driven decisions</span>, supported by intelligent systems that optimize resources and anticipate market needs." },
    'vision-text-2': { it: "Creare un ecosistema di <span class=\"highlight\">soluzioni accessibili</span> e integrate che rendano l'automazione e l'analisi avanzata una leva strategica quotidiana, liberando potenziale umano per compiti a maggior valore aggiunto.", en: "Creating an ecosystem of <span class=\"highlight\">accessible</span> and integrated solutions that make automation and advanced analysis a daily strategic lever, freeing up human potential for higher value-added tasks." },
    'vision-quote': { it: "\"L'efficienza non è fare di più, ma fare meglio ciò che conta davvero, guidati dai dati.\"", en: "\"Efficiency is not about doing more, but doing better what truly matters, guided by data.\"" },

    // Services Section
    'services-subtitle': { it: "Soluzioni integrate per ottimizzare l'organizzazione, sfruttare i dati e automatizzare i processi della tua PMI.", en: "Integrated solutions to optimize organization, leverage data, and automate processes for your SME." },
    'service1-title': { it: "Data Intelligence & Reporting Strategico", en: "Data Intelligence & Strategic Reporting" },
    'service1-desc': { it: "Trasformiamo i tuoi dati grezzi in conoscenza azionabile. Sviluppiamo dashboard interattive (Power BI, Looker Studio, ecc.) e report chiari per monitorare performance, identificare trend e supportare decisioni strategiche informate.", en: "We transform your raw data into actionable knowledge. We develop interactive dashboards (Power BI, Looker Studio, etc.) and clear reports to monitor performance, identify trends, and support informed strategic decisions." },
    'service1-feature1': { it: "Cruscotti Decisionali KPI", en: "KPI Decision Dashboards" },
    'service1-feature2': { it: "Analisi Esplorativa & Diagnostica", en: "Exploratory & Diagnostic Analysis" },
    'service1-feature3': { it: "Reportistica Efficace e Puntuale", en: "Effective and Timely Reporting" },
    'service2-title': { it: "Ottimizzazione & Automazione Processi", en: "Process Optimization & Automation" },
    'service2-desc': { it: "Mappiamo, ridisegniamo e automatizziamo i flussi di lavoro ripetitivi. Implementiamo soluzioni (low-code/scripting) per connettere sistemi, eliminare colli di bottiglia, ridurre errori e liberare tempo prezioso.", en: "We map, redesign, and automate repetitive workflows. We implement solutions (low-code/scripting) to connect systems, eliminate bottlenecks, reduce errors, and free up valuable time." },
    'service2-feature1': { it: "Integrazione Sistemi Aziendali", en: "Business Systems Integration" },
    'service2-feature2': { it: "Automazione Task Manuali", en: "Manual Task Automation" },
    'service2-feature3': { it: "Workflow Digitali Intelligenti", en: "Intelligent Digital Workflows" },
    'service3-title': { it: "Consulenza Organizzativa & Data Strategy", en: "Organizational Consulting & Data Strategy" },
    'service3-desc': { it: "Supporto strategico per definire la roadmap verso un'organizzazione data-driven. Aiutiamo a scegliere tecnologie adatte, strutturare la gestione dei dati, garantire qualità e compliance, e promuovere una cultura dell'efficienza basata sui fatti.", en: "Strategic support to define the roadmap towards a data-driven organization. We help choose suitable technologies, structure data management, ensure quality and compliance, and promote a culture of fact-based efficiency." },
    'service3-feature1': { it: "Assessment Maturità Organizzativa/Dati", en: "Organizational/Data Maturity Assessment" },
    'service3-feature2': { it: "Disegno Architetture Dati Sostenibili", en: "Sustainable Data Architecture Design" },
    'service3-feature3': { it: "Affiancamento e Formazione Team", en: "Team Coaching and Training" },

    // Portfolio Section
    'portfolio-subtitle': { it: "Esempi concreti di come abbiamo aiutato le aziende a organizzarsi meglio, decidere con i dati e automatizzare per crescere.", en: "Concrete examples of how we have helped companies organize better, decide with data, and automate for growth." },
    'portfolio1-title': { it: "Analisi Strategica Clienti Bikesharing (Base Google Cert.)", en: "Strategic Customer Analysis for Bikesharing (Google Cert. Based)" },
    'portfolio1-desc': { it: "Studio approfondito per segmentare la clientela, identificare driver di utilizzo e suggerire azioni mirate per aumentare retention e conversioni. Realizzato con R.", en: "In-depth study to segment customers, identify usage drivers, and suggest targeted actions to increase retention and conversions. Created with R." },
    'tag-r': { it: 'R', en: 'R' },
    'tag-analysis': { it: 'Analisi Dati', en: 'Data Analysis' },
    'tag-segmentation': { it: 'Segmentazione', en: 'Segmentation' },
    'tag-strategy': { it: 'Strategia', en: 'Strategy' },
    'portfolio-view-details': { it: 'Vedi Analisi', en: 'View Analysis' },
    'portfolio2-title': { it: "Cruscotto Interattivo Performance Aziendale", en: "Interactive Business Performance Dashboard" },
    'portfolio2-desc': { it: "Sviluppo dashboard Power BI per monitoraggio integrato KPI vendite, marketing e operations. Analisi profittabilità e identificazione aree miglioramento.", en: "Development of Power BI dashboard for integrated monitoring of sales, marketing, and operations KPIs. Profitability analysis and identification of improvement areas." },
    'tag-powerbi': { it: 'Power BI', en: 'Power BI' },
    'tag-sql': { it: 'SQL', en: 'SQL' },
    'tag-bi': { it: 'BI', en: 'BI' },
    'tag-kpi': { it: 'KPI Monitoring', en: 'KPI Monitoring' },
    'portfolio-view-live': { it: 'Vedi Demo', en: 'View Demo' },
    'portfolio3-title': { it: "Automazione Flusso Dati e Reportistica", en: "Data Flow Automation and Reporting" },
    'portfolio3-desc': { it: "Workflow automatizzato (Python/low-code) per estrarre dati da sorgenti multiple, consolidarli, generare report periodici e distribuirli ai team.", en: "Automated workflow (Python/low-code) to extract data from multiple sources, consolidate it, generate periodic reports, and distribute them to teams." },
    'tag-python': { it: 'Python', en: 'Python' },
    'tag-automation': { it: 'Automazione', en: 'Automation' },
    'tag-etl': { it: 'ETL', en: 'ETL' },
    'tag-workflow': { it: 'Workflow', en: 'Workflow' },
    'portfolio-view-code': { it: 'Vedi Approccio', en: 'View Approach' },

    // Certifications Section
    'cert-subtitle': { it: "Una base solida e un impegno costante nell'aggiornamento per offrire soluzioni sempre all'avanguardia nel campo dei dati e dell'efficienza organizzativa.", en: "A solid foundation and a constant commitment to updating to offer cutting-edge solutions in the field of data and organizational efficiency." },
    'cert1-title': { it: "Google Data Analytics Professional Certificate", en: "Google Data Analytics Professional Certificate" },
    'cert1-issuer': { it: "Rilasciato da Google (via Coursera)", en: "Issued by Google (via Coursera)" },
    'cert1-desc': { it: "Fondamenta metodologiche nell'intero ciclo di vita dell'analisi dati: raccolta, pulizia, analisi (SQL, R), visualizzazione (es. Tableau), interpretazione e comunicazione degli insight.", en: "Methodological foundations in the entire data analysis lifecycle: collection, cleaning, analysis (SQL, R), visualization (e.g., Tableau), interpretation, and communication of insights." },
    'cert-verify': { it: "Verifica Credenziale", en: "Verify Credential" },
    'skill1-title': { it: "Competenze in Automazione Low-Code & Scripting", en: "Skills in Low-Code Automation & Scripting" },
    'skill1-issuer': { it: "Esperienza Pratica", en: "Practical Experience" },
    'skill1-desc': { it: "Capacità di progettare e implementare workflow automatizzati utilizzando piattaforme low-code/no-code e scripting (Python) per l'integrazione di API e l'automazione di task.", en: "Ability to design and implement automated workflows using low-code/no-code platforms and scripting (Python) for API integration and task automation." },

    // Contacts Section
    'contacts-subtitle': { it: "Pronto a migliorare l'organizzazione e l'efficienza della tua PMI? Raccontaci le tue sfide o richiedi una consulenza preliminare gratuita.", en: "Ready to improve the organization and efficiency of your SME? Tell us about your challenges or request a free preliminary consultation." },
    'contact-form-title': { it: "Invia la tua richiesta", en: "Send Your Request" },
    'form-name': { it: "Nome", en: "Name" },
    'form-email': { it: "Email Aziendale", en: "Business Email" },
    'form-subject': { it: "Oggetto", en: "Subject" },
    'form-message': { it: "Descrivi la tua esigenza", en: "Describe your need" },
    'form-submit': { it: "Invia Richiesta", en: "Send Request" },
    'contact-info-title': { it: "Informazioni Dirette", en: "Direct Information" },
    'contact-email-label': { it: "Email", en: "Email" },
    'contact-email-value': { it: "contatti@osaide.placeholder.com", en: "contacts@osaide.placeholder.com" },
    'contact-linkedin-label': { it: "LinkedIn", en: "LinkedIn" },
    'contact-linkedin-value': { it: "Profilo OSAIDE (Placeholder)", en: "OSAIDE Profile (Placeholder)" },
    'contact-github-label': { it: "GitHub", en: "GitHub" },
    'contact-github-value': { it: "Repository Progetti (Placeholder)", en: "Project Repositories (Placeholder)" },
    'contact-location-label': { it: "Operatività", en: "Operations" },
    'contact-location-value': { it: "Italia (Remoto & On-site su progetto)", en: "Italy (Remote & On-site by project)" },

    // Chatbot Demo Section
    'chatbot-demo-subtitle': {
        it: "Prova in anteprima alcune delle capacità di automazione e interazione intelligente. Qui potrai testare chatbot personalizzati sviluppati con Streamlit e integrati con logiche backend (es. n8n) per mostrarti il potenziale per la tua attività.",
        en: "Preview some of the automation and intelligent interaction capabilities. Here you can test custom chatbots developed with Streamlit and integrated with backend logic (e.g., n8n) to show you the potential for your business."
    },
    'chatbot-demo1-title': { it: 'Demo 1: Assistente Virtuale FAQ', en: 'Demo 1: FAQ Virtual Assistant' },
    'chatbot-demo1-desc': {
        it: "Un esempio di chatbot addestrato a rispondere alle domande frequenti su un prodotto o servizio. Utile per alleggerire il carico del customer service e fornire risposte immediate h24.",
        en: "An example of a chatbot trained to answer frequently asked questions about a product or service. Useful for reducing customer service load and providing immediate 24/7 responses."
    },
    'chatbot-demo-iframe-note': {
        it: "Lo spazio soprastante è predisposto per ospitare un'applicazione chatbot interattiva.",
        en: "The space above is set up to host an interactive chatbot application."
    },
    'chatbot-demo2-title': { it: 'Demo 2: Raccoglitore Lead Qualificato', en: 'Demo 2: Qualified Lead Collector' },
    'chatbot-demo2-desc': {
        it: "Questo chatbot è progettato per interagire con i visitatori del sito, qualificare i lead ponendo domande specifiche e, se opportuno, raccogliere informazioni di contatto per un follow-up.",
        en: "This chatbot is designed to interact with site visitors, qualify leads by asking specific questions, and, if appropriate, collect contact information for follow-up."
    },
    'chatbot-demo-iframe-note2': {
        it: "Questo iframe attende l'URL dell'applicazione Streamlit per il secondo demo.",
        en: "This iframe awaits the Streamlit application URL for the second demo."
    },

    // Footer
    'footer-copyright': { it: "&copy; <span id=\"current-year\"></span> OSAIDE. Tutti i diritti riservati.", en: "&copy; <span id=\"current-year\"></span> OSAIDE. All rights reserved." },
    'footer-privacy': { it: "Privacy Policy", en: "Privacy Policy" },
    'footer-cookie': { it: "Cookie Policy", en: "Cookie Policy" },

    // Scroll Invitation
    'scroll-invite-text': { it: 'Scorri per scoprire di più', en: 'Scroll to discover more' }
};

// --- Funzioni Lingua --- Define at top level
const htmlEl = document.documentElement;

function setLanguage(lang) {
    htmlEl.setAttribute('lang', lang);
    document.querySelectorAll('[data-key]').forEach(element => {
        const key = element.getAttribute('data-key');
        if (translations[key] && translations[key][lang]) {
            if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                if (element.placeholder) element.placeholder = translations[key][lang];
            } else {
                element.innerHTML = translations[key][lang];
            }
        }
    });
    updateFormPlaceholders(lang); // Ensure form placeholders are updated if they are part of translations
    localStorage.setItem('language', lang);
}

function updateFormPlaceholders(lang) {
    // This function might be redundant if all placeholders are handled by data-key,
    // but kept if there are specific cases or future needs.
    // Example:
    // const namePlaceholder = translations['form-name-placeholder'] ? translations['form-name-placeholder'][lang] : 'Il tuo nome';
    // const emailPlaceholder = translations['form-email-placeholder'] ? translations['form-email-placeholder'][lang] : 'latuaemail@azienda.com';
    // if(document.getElementById('name')) document.getElementById('name').placeholder = namePlaceholder;
    // if(document.getElementById('email')) document.getElementById('email').placeholder = emailPlaceholder;
}


// --- Main DOMContentLoaded Event Listener ---
document.addEventListener('DOMContentLoaded', () => {
    // --- Hamburger Menu Logic ---
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const menuOverlay = document.getElementById('menu-overlay');
    const navLinksMobile = sidebar.querySelectorAll('.nav-link');

    if (menuToggle && sidebar && menuOverlay) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-active');
            menuOverlay.classList.toggle('active');
            menuToggle.setAttribute('aria-expanded', sidebar.classList.contains('mobile-active'));
        });
        menuOverlay.addEventListener('click', () => {
            sidebar.classList.remove('mobile-active');
            menuOverlay.classList.remove('active');
            menuToggle.setAttribute('aria-expanded', 'false');
        });
        navLinksMobile.forEach(link => {
            link.addEventListener('click', () => {
                if (sidebar.classList.contains('mobile-active')) { // Only close if mobile menu is active
                    sidebar.classList.remove('mobile-active');
                    menuOverlay.classList.remove('active');
                    menuToggle.setAttribute('aria-expanded', 'false');
                }
            });
        });
    }

    // --- Active Nav Link on Scroll & Scroll Invitation Logic ---
    const sections = document.querySelectorAll('.section');
    const navLinks = document.querySelectorAll('.nav-link');
    const scrollInvitation = document.getElementById('scroll-invitation');
    const lastContentSectionId = 'chatbot-demo'; // Or verify this ID is correct for the actual last section

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.4
    };

    const sectionObserver = new IntersectionObserver((entries, observer) => {
        let intersectedSectionId = null;
        let isLastSectionVisible = false;

        entries.forEach(entry => {
            if (entry.isIntersecting) {
                intersectedSectionId = entry.target.id;
                if (entry.target.id === lastContentSectionId) {
                    isLastSectionVisible = true;
                }
            }
        });

        if (intersectedSectionId) {
            const targetHref = `#${intersectedSectionId}`;
            navLinks.forEach(link => {
                if (link.getAttribute('href') === targetHref) {
                    link.classList.add('active');
                } else {
                    link.classList.remove('active');
                }
            });
        }

        if (scrollInvitation) {
            if (isLastSectionVisible || !intersectedSectionId) {
                scrollInvitation.classList.remove('opacity-100');
                scrollInvitation.classList.add('opacity-0');
            } else {
                scrollInvitation.classList.remove('opacity-0');
                scrollInvitation.classList.add('opacity-100');
            }
        }
    }, observerOptions);

    if (sections.length > 0) { // Only observe if sections exist
        sections.forEach(section => {
            sectionObserver.observe(section);
        });
    }

    // --- Copyright Year ---
    const currentYearElement = document.getElementById('current-year');
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    }

    // --- Contact Form Handling (Placeholder) ---
    const contactForm = document.getElementById('contact-form');
    const formStatus = document.getElementById('form-status');
    if (contactForm && formStatus) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();
            console.log('Form submitted (placeholder)');
            formStatus.textContent = 'Invio in corso...'; // Example: Use translation key if this text needs to be translated
            formStatus.className = 'mt-4 text-center text-sm text-yellow-400';
            setTimeout(() => {
                formStatus.textContent = 'Messaggio inviato con successo!'; // Example: Use translation key
                formStatus.className = 'mt-4 text-center text-sm text-green-400';
                contactForm.reset();
                setTimeout(() => {
                    formStatus.textContent = '';
                    formStatus.className = 'mt-4 text-center text-sm';
                }, 3000);
            }, 1500);
        });
    }

    // --- Inizializza Neon Cursor ---
    try {
        neonCursor({
            el: document.getElementById('cursor-container'),
            shaderPoints: 12,
            curvePoints: 60,
            curveLerp: 0.6,
            radius1: 3,
            radius2: 15,
            velocityTreshold: 15,
            sleepRadiusX: 150,
            sleepRadiusY: 150,
            sleepTimeCoefX: 0.0025,
            sleepTimeCoefY: 0.0025,
        });
        console.log("Neon Cursor Initialized with adjusted parameters on #cursor-container.");
    } catch (error) {
        console.error("Failed to initialize Neon Cursor on #cursor-container:", error);
    }

    // --- Initial Active Nav Link & Language Setup ---
    // Imposta Home come attivo inizialmente (ritardato) se nessuna sezione è già attiva
     setTimeout(() => {
         const isActiveLinkPresent = document.querySelector('.nav-link.active');
         if (!isActiveLinkPresent && sections.length > 0 && window.location.hash === '' || window.location.hash === '#home' || !document.querySelector(window.location.hash)) {
            // Check if first section is visible (or home is targeted)
            const firstSection = document.querySelector('.section');
            if (firstSection) {
                 const firstSectionTop = firstSection.getBoundingClientRect().top;
                 const firstSectionBottom = firstSection.getBoundingClientRect().bottom;
                 const viewportHeight = window.innerHeight;
                 // Check if at least a part of the first section is visible
                 if ( (firstSectionTop < viewportHeight && firstSectionBottom > 0) || window.location.hash === '#home' ) {
                    const homeLink = document.querySelector('.nav-link[href="#home"]');
                    if (homeLink) {
                        navLinks.forEach(link => link.classList.remove('active')); // Clear others
                        homeLink.classList.add('active');
                    }
                 }
            }
         } else if (isActiveLinkPresent && window.location.hash && document.querySelector(window.location.hash) ) {
            // If a hash is present and an active link is already set by observer, ensure it matches the hash
            // Or if observer hasn't run, set based on hash
            const currentHashLink = document.querySelector(`.nav-link[href="${window.location.hash}"]`);
            if(currentHashLink && !currentHashLink.classList.contains('active')) {
                navLinks.forEach(link => link.classList.remove('active'));
                currentHashLink.classList.add('active');
            }
         }
     }, 150); // Increased timeout slightly for observer to potentially run first

    // Initial call to setLanguage
    const currentSavedLang = localStorage.getItem('language') || 'it';
    setLanguage(currentSavedLang);
});
