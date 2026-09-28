import { FormEvent, ReactNode, useMemo, useState } from "react";

type IconName =
  | "arrow"
  | "calendar"
  | "check"
  | "chevron"
  | "clock"
  | "grid"
  | "ink"
  | "list"
  | "plus"
  | "search"
  | "spark"
  | "user";

const Icon = ({ name, className = "size-5" }: { name: IconName; className?: string }) => {
  const paths: Record<IconName, ReactNode> = {
    arrow: <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
    calendar: <><path d="M8 2v4M16 2v4M3 10h18" /><rect x="3" y="4" width="18" height="18" rx="2" /></>,
    check: <path d="m5 12 4 4L19 6" />,
    chevron: <path d="m9 18 6-6-6-6" />,
    clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
    grid: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
    ink: <><path d="M14.5 4.5 19 9 9 19H4.5v-4.5l10-10Z" /><path d="m12 7 5 5M4.5 19 3 21l2-1" /></>,
    list: <><path d="M9 6h11M9 12h11M9 18h11" /><path d="M4 6h.01M4 12h.01M4 18h.01" /></>,
    plus: <path d="M12 5v14M5 12h14" />,
    search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
    spark: <><path d="m12 3 1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3Z" /><path d="m5 15 .8 2.2L8 18l-2.2.8L5 21l-.8-2.2L2 18l2.2-.8L5 15Z" /></>,
    user: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
  };

  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {paths[name]}
    </svg>
  );
};

type FlashName = "dagger" | "eye" | "moth" | "rose" | "serpent" | "skull";

const FlashArt = ({
  name,
  className = "size-32",
  fillFrame = false,
}: {
  name: FlashName;
  className?: string;
  fillFrame?: boolean;
}) => {
  const art: Record<FlashName, ReactNode> = {
    dagger: (
      <>
        <path d="M80 15 94 43 86 50v62l17 13-23 22-23-22 17-13V50l-8-7 14-28Z" />
        <path d="M80 50v79M55 55h50M64 48l-17 7 17 7M96 48l17 7-17 7M68 125h24" />
        <path d="m72 36 8-12 8 12-8 8-8-8Z" />
      </>
    ),
    eye: (
      <>
        <path d="M17 82s24-37 63-37 63 37 63 37-24 36-63 36S17 82 17 82Z" />
        <circle cx="80" cy="82" r="22" />
        <circle cx="80" cy="82" r="8" fill="currentColor" />
        <path d="M28 44 17 29M49 33l-6-20M80 29V7M111 33l6-20M132 44l11-15M28 120l-11 15M49 131l-6 20M80 135v18M111 131l6 20M132 120l11 15" />
      </>
    ),
    moth: (
      <>
        <path d="M80 43c-8-15-27-26-46-21 1 27 12 44 35 52-26-2-43 9-52 28 18 15 38 17 58 4" />
        <path d="M80 43c8-15 27-26 46-21-1 27-12 44-35 52 26-2 43 9 52 28-18 15-38 17-58 4" />
        <path d="M80 38c-9 10-10 69 0 93 10-24 9-83 0-93ZM72 37 62 20M88 37l10-17" />
        <path d="M34 35c13 5 22 14 28 28M23 96c17-6 31-5 44 4M126 35c-13 5-22 14-28 28M137 96c-17-6-31-5-44 4" />
        <circle cx="80" cy="79" r="4" fill="currentColor" />
      </>
    ),
    rose: (
      <>
        <path d="M80 29c17-16 37 2 27 17 22-5 31 19 14 30 18 8 10 34-10 32-2 19-27 23-36 7-14 14-36 0-29-18-21-4-29-31-8-38-14-14 2-37 21-28 3-19 28-22 42-9Z" />
        <path d="M80 47c17-12 31 8 18 20 15 4 12 25-3 27-6 15-29 10-28-6-15-6-9-28 7-27-4-6-1-11 6-14Z" />
        <path d="M78 63c12-2 18 13 9 21-10 8-24-2-18-13M67 115l-9 31M88 118l9 28M60 132l-17-9M95 133l19-10" />
      </>
    ),
    skull: (
      <>
        <path d="M80 14c-34 0-57 25-57 59 0 22 10 39 27 49v19l13-7 8 12 9-10 9 10 8-12 13 7v-19c17-10 27-27 27-49 0-34-23-59-57-59Z" />
        <path d="M30 86c-12-4-16 6-11 16 4 9 13 14 23 12M130 86c12-4 16 6 11 16-4 9-13 14-23 12" />
        <path d="M44 70c4-17 26-20 32-3 4 13-6 25-20 23-11-1-16-10-12-20ZM116 70c-4-17-26-20-32-3-4 13 6 25 20 23 11-1 16-10 12-20Z" />
        <path d="m80 82-9 24 9 8 9-8-9-24ZM49 122l7 10M63 119l4 17M97 119l-4 17M111 122l-7 10" />
        <path d="M58 105c13 7 31 7 44 0M58 39c13-10 31-13 45-4M80 15l-4 17 9 7-8 14" />
        <path d="M39 55c-9-8-14-18-15-30M121 55c9-8 14-18 15-30M51 29 43 15M109 29l8-14" />
        <circle cx="58" cy="71" r="6" fill="currentColor" />
        <circle cx="102" cy="71" r="6" fill="currentColor" />
      </>
    ),
    serpent: (
      <>
        <path d="M105 26c-23-13-50 5-47 29 3 25 40 24 42 49 1 19-20 34-39 25-11-5-15-18-10-29" />
        <path d="M113 23c10 4 18 13 20 24l-22-5-15 16-2-24 19-11Z" />
        <path d="M127 45 143 55M76 45c-7 2-12 7-12 13M87 82c7 4 12 10 12 17M65 123c-7-4-10-12-7-20" />
        <path d="M65 57c9-4 18-3 26 3M97 99c-7 3-14 3-22-1M52 101c7 1 13 5 17 11" />
        <circle cx="116" cy="34" r="2.5" fill="currentColor" />
      </>
    ),
  };

  return (
    <svg
      viewBox="0 0 160 160"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      preserveAspectRatio={fillFrame ? "xMidYMid slice" : "xMidYMid meet"}
      aria-hidden="true"
    >
      {art[name]}
    </svg>
  );
};

function InkBackdrop({ light = false }: { light?: boolean }) {
  const tone = light ? "text-rust" : "text-ember";
  const secondary = light ? "text-ink" : "text-cream";

  return (
    <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden="true">
      <img
        src={new URL("./imports/download2-1.jfif", import.meta.url).href}
        alt=""
        className={`absolute left-1/2 top-1/2 h-full w-full -translate-x-1/2 -translate-y-1/2 scale-125 object-contain ${
          light ? "opacity-15 mix-blend-multiply" : "opacity-20 invert mix-blend-screen"
        }`}
      />

      <svg
        viewBox="0 0 1200 250"
        className={`absolute left-1/2 top-0 w-full min-w-max -translate-x-1/2 ${tone} opacity-25`}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M0 57c116 3 182 29 198 78 13 40-31 67-63 42-29-23-9-64 29-53 53 16 67 85 135 85 60 0 79-54 137-54 64 0 88 66 164 66s100-66 164-66c58 0 77 54 137 54 68 0 82-69 135-85 38-11 58 30 29 53-32 25-76-2-63-42 16-49 82-75 198-78" />
        <path d="M168 123c-22-31-54-47-96-47M1032 123c22-31 54-47 96-47M241 183c-30-3-54-16-73-39M959 183c30-3 54-16 73-39" />
        <path d="M366 174c-31-28-37-58-19-90 38 7 58 30 59 69M834 174c31-28 37-58 19-90-38 7-58 30-59 69" />
        <path d="M397 151c-4-31 8-55 35-71 26 24 32 50 17 78M803 151c4-31-8-55-35-71-26 24-32 50-17 78" />
        <path d="M476 173c34-14 57-41 69-80 28 30 46 71 55 123 9-52 27-93 55-123 12 39 35 66 69 80" />
        <path d="M561 104c-17-31-12-61 15-89 17 19 25 41 24 66-1-25 7-47 24-66 27 28 32 58 15 89" />
        <path d="M547 192c17-19 34-29 53-29s36 10 53 29M600 163v58" />
        <circle cx="600" cy="132" r="7" />
      </svg>

      <svg
        viewBox="0 0 360 900"
        className={`absolute -left-20 top-24 h-4/5 w-auto ${tone} opacity-30`}
        fill="none"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M52 6c56 92 63 191 29 298-28 91-10 186 55 285 43 65 55 164 35 296" />
        <path d="M72 120c48-24 85-57 110-99M88 252c-39-18-66-45-83-80M97 395c60-28 105-70 134-126M121 560c-49-24-84-59-106-105M151 728c55-24 96-61 122-111" />
        <path d="M106 72c-19-33-7-59 28-78 32 14 44 38 35 72-16-12-37-10-63 6Z" />
        <path d="m126 24-25-17 30 3M139 18l18-19-8 28M116 46c16 7 29 7 40 0" />
        <path d="M49 197c-32-30-29-62 9-96 43 7 64 32 62 74-23-10-47-2-71 22Z" />
        <path d="m66 132-29-9 31-4M80 126l10-25 1 29M57 163c19 3 34-1 44-12" />
        <path d="M157 330c27-37 60-42 100-16 3 44-17 70-59 80 5-25-9-46-41-64Z" />
        <path d="m223 344 20-25-5 33M230 358l27 4-28 8M189 349c1 19 8 32 23 40" />
        <path d="M72 478c-35-32-33-66 6-102 46 6 69 32 67 77-25-11-49-2-73 25Z" />
        <path d="m92 410-32-10 34-4M108 405l10-28 2 31M81 444c19 4 35-1 47-13" />
        <path d="M190 670c30-39 65-44 108-15 2 47-20 75-64 84 6-26-9-49-44-69Z" />
        <path d="m259 685 21-27-5 35M266 701l29 5-30 8M225 691c0 19 8 34 23 42" />
        <path d="M174 803c17 4 29 14 36 30-17 8-32 6-45-7M168 778c-15-2-29 3-41 16 12 13 25 17 40 11M127 596c-15-1-28 5-39 18 13 12 27 15 41 8M125 528c16 1 29-5 40-19-14-11-28-14-42-6M92 316c-16-3-30 2-43 14 11 14 25 19 40 14M88 280c16 1 30-5 40-19-14-12-29-14-43-6M64 155c-15-3-29 1-42 13 11 14 24 19 40 15" />
      </svg>

      <svg
        viewBox="0 0 420 760"
        className={`absolute -right-28 bottom-0 h-3/4 w-auto ${secondary} opacity-15`}
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M214 742c-26-119 20-203 139-252M219 650c-45-20-79-53-102-100M247 598c39-17 68-44 87-80" />
        <path d="M288 491c-34-75-17-130 51-166 66 40 76 97 29 170-24-37-51-38-80-4Z" />
        <path d="M316 445c-26-42-19-73 21-95 43 18 52 50 27 96-12-25-28-25-48-1Z" />
        <path d="M335 393c12-19 27-24 44-15-2 20-12 31-32 33" />
        <path d="M351 325c-15-31-11-57 12-79M329 328c-28-21-40-47-35-78M375 339c13-29 34-46 65-52" />
        <path d="M297 488c-45 10-72 43-80 100M363 488c27 20 39 47 36 81" />
        <path d="M215 650c-32-17-63-11-91 18l-28-5-36 22 20 29 42-8 29 13 30-9 34-60Z" />
        <path d="m81 686-38-6-25 16 31 13 31 5M122 706l-10 37M151 717l7 31M181 704l22 29" />
        <path d="M111 665c10-25 25-40 46-45l31 13M135 659l28 18M159 641l26 14" />
        <circle cx="105" cy="686" r="8" />
        <path d="M268 550c-23-30-20-59 8-87M245 581c-35-15-51-41-48-78M306 530c7-35 29-56 64-63" />
      </svg>

      <svg
        viewBox="0 0 900 220"
        className={`absolute bottom-0 left-1/2 w-4/5 -translate-x-1/2 ${tone} opacity-20`}
        fill="none"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
      >
        <path d="M0 204c77-11 119-47 126-108 5-42-41-47-48-12-7 34 43 47 79 18 42-34 66-83 52-102M900 204c-77-11-119-47-126-108-5-42 41-47 48-12 7 34-43 47-79 18-42-34-66-83-52-102" />
        <path d="M119 133c91 58 176 47 255-34 30-31 55-37 76-17 21-20 46-14 76 17 79 81 164 92 255 34" />
        <path d="M276 154c44-1 76-17 96-48M624 154c-44-1-76-17-96-48M399 113c15 4 32 20 51 48 19-28 36-44 51-48M425 174l25 38 25-38" />
      </svg>
    </div>
  );
}

function CornerOrnaments({
  className = "",
  compact = false,
}: {
  className?: string;
  compact?: boolean;
}) {
  const cornerClass = compact ? "size-10" : "size-16";
  const flourish = (
    <>
      <path d="M4 73C6 36 25 10 66 5" />
      <path d="M7 56c17 2 29-6 36-25 12 7 17 17 15 30" />
      <path d="M20 35C13 24 16 15 29 8c10 9 11 19 4 29" />
      <path d="M8 69c11-14 24-18 39-12" />
    </>
  );

  return (
    <div className={`pointer-events-none absolute inset-0 text-ember ${className}`} aria-hidden="true">
      <svg viewBox="0 0 80 80" className={`absolute left-2 top-2 ${cornerClass}`} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">{flourish}</svg>
      <svg viewBox="0 0 80 80" className={`absolute right-2 top-2 rotate-90 ${cornerClass}`} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">{flourish}</svg>
      <svg viewBox="0 0 80 80" className={`absolute bottom-2 right-2 rotate-180 ${cornerClass}`} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">{flourish}</svg>
      <svg viewBox="0 0 80 80" className={`absolute bottom-2 left-2 -rotate-90 ${cornerClass}`} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">{flourish}</svg>
    </div>
  );
}

const NativeButton = "button";
const NativeInput = "input";
const NativeTextarea = "textarea";
const NativeSelect = "select";

function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "outline" | "quiet";
}) {
  const variants = {
    primary: "bg-ember text-ink shadow-xl hover:bg-ember-bright",
    ghost: "text-smoke hover:bg-paper/6 hover:text-cream",
    outline: "border border-line text-cream hover:border-smoke hover:bg-paper/5",
    quiet: "bg-paper/6 text-cream hover:bg-paper/10",
  };
  return (
    <NativeButton
      className={`inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold transition duration-200 disabled:cursor-not-allowed disabled:opacity-40 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </NativeButton>
  );
}

const Field = ({
  label,
  hint,
  light = false,
  children,
}: {
  label: string;
  hint?: string;
  light?: boolean;
  children: ReactNode;
}) => (
  <label className="grid gap-2">
    <span className={`text-sm font-medium ${light ? "text-ink" : "text-cream"}`}>{label}</span>
    {children}
    {hint && <span className={`text-xs ${light ? "text-stone" : "text-smoke"}`}>{hint}</span>}
  </label>
);

type Stage = "Pedida" | "Desenho aprovado" | "Em sessões" | "Finalizada";

type Tattoo = {
  id: number;
  client: string;
  initials: string;
  title: string;
  placement: string;
  size: string;
  stage: Stage;
  next: string;
  artist: string;
  accent: string;
};

const initialTattoos: Tattoo[] = [
  { id: 1, client: "Bruna Maia", initials: "BM", title: "Jardim botânico", placement: "Costela esquerda", size: "28 cm", stage: "Em sessões", next: "Sessão 02 · 18 Jun, 14h", artist: "Vitor", accent: "bg-olive" },
  { id: 2, client: "Caio Nunes", initials: "CN", title: "Serpente ornamental", placement: "Antebraço", size: "22 cm", stage: "Desenho aprovado", next: "Agendar primeira sessão", artist: "Vitor", accent: "bg-rust" },
  { id: 3, client: "Lia Torres", initials: "LT", title: "Mariposa lunar", placement: "Nuca", size: "12 cm", stage: "Pedida", next: "Revisar briefing", artist: "Nina", accent: "bg-plum" },
  { id: 4, client: "Rafael Lima", initials: "RL", title: "Linhas do horizonte", placement: "Panturrilha", size: "18 cm", stage: "Finalizada", next: "Concluída em 03 Jun", artist: "Nina", accent: "bg-slate" },
];

const stageStyle: Record<Stage, string> = {
  Pedida: "bg-sand/10 text-sand border-sand/20",
  "Desenho aprovado": "bg-rust/15 text-copper border-rust/30",
  "Em sessões": "bg-olive/20 text-sage border-olive/40",
  Finalizada: "bg-paper/8 text-smoke border-paper/10",
};

function Brand({ light = false }: { light?: boolean }) {
  return (
    <div className="relative flex items-center gap-3 px-2 py-1">
      <CornerOrnaments className="-inset-2 opacity-40" compact />
      <div className="grid size-10 place-items-center rounded-full border border-ember/50 text-ember">
        <Icon name="ink" className="size-5" />
      </div>
      <div>
        <div className={`font-display text-2xl leading-none tracking-wide ${light ? "text-ink" : "text-cream"}`}>Tinta Negra</div>
        <div className={`mt-1 text-xs font-bold uppercase tracking-[0.32em] ${light ? "text-stone" : "text-smoke"}`}>Tattoo Studio</div>
      </div>
    </div>
  );
}

function StagePill({ stage }: { stage: Stage }) {
  return <span className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold ${stageStyle[stage]}`}>{stage}</span>;
}

function ArtistApp() {
  const [filter, setFilter] = useState<Stage | "Todas">("Todas");
  const [tattoos, setTattoos] = useState(initialTattoos);
  const [selectedId, setSelectedId] = useState(1);
  const [showStep, setShowStep] = useState(false);
  const [saved, setSaved] = useState(false);
  const selected = tattoos.find((tattoo) => tattoo.id === selectedId) ?? tattoos[0];
  const visible = useMemo(
    () => tattoos.filter((tattoo) => filter === "Todas" || tattoo.stage === filter),
    [filter, tattoos],
  );

  function saveStep(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const step = data.get("step");
    const stage: Stage = step === "Retoque" ? "Finalizada" : step === "Desenho aprovado" ? "Desenho aprovado" : "Em sessões";
    setTattoos((items) => items.map((item) => item.id === selected.id ? { ...item, stage, next: stage === "Finalizada" ? "Projeto concluído" : "Próximo passo a definir" } : item));
    setShowStep(false);
    setSaved(true);
    window.setTimeout(() => setSaved(false), 2600);
  }

  const filters: Array<Stage | "Todas"> = ["Todas", "Pedida", "Desenho aprovado", "Em sessões", "Finalizada"];

  return (
    <div className="min-h-screen bg-ink text-cream">
      <InkBackdrop />
      <header className="sticky top-0 z-30 flex h-20 items-center justify-between overflow-hidden border-b border-line bg-ink/90 px-5 backdrop-blur-xl lg:hidden">
        <div className="relative z-10"><Brand /></div>
        <img
          src={new URL("./imports/download-1.jfif", import.meta.url).href}
          alt=""
          className="pointer-events-none absolute left-1/2 top-0 h-120 w-60 -translate-x-1/2 -translate-y-1/2 -rotate-90 object-contain opacity-25 invert mix-blend-screen"
        />
        <div className="relative z-10">
          <svg
            viewBox="0 0 150 110"
            className="pointer-events-none absolute -right-5 -top-8 h-24 w-32 text-ember"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M82 72C63 66 48 53 39 33M88 72c17-14 25-30 24-49M75 75C52 79 34 92 21 110M92 76c17 5 31 16 43 34" />
            <path d="M40 34c-7-1-12-6-15-13 8-3 15-1 19 6 1-8 6-13 14-14 3 8 1 15-6 20 8 0 13 4 16 11-7 5-14 5-21-1-3 8-8 12-16 12-2-8 1-15 9-21Z" />
            <circle cx="43" cy="34" r="4" fill="currentColor" />
            <path d="M112 24c-6-3-10-8-10-15 8-1 14 2 17 9 3-7 8-11 16-10 1 8-2 14-10 17 7 2 12 7 13 14-8 3-14 1-19-6-4 6-10 9-18 7 0-8 4-13 11-16Z" />
            <circle cx="119" cy="24" r="4" fill="currentColor" />
            <path d="M41 92c-9-2-16 0-22 6 8 5 15 5 23 0M113 94c9-3 17-1 23 5-8 6-16 6-24 1M62 62c-7-8-15-10-24-7 4 9 11 13 21 12M101 56c8-7 16-8 25-4-5 9-13 12-22 10" />
          </svg>
          <div className="relative grid size-10 place-items-center rounded-full border border-ember-bright bg-ember text-sm font-bold text-ink shadow-xl">VS</div>
        </div>
      </header>

      <aside className="fixed inset-y-0 left-0 z-40 hidden w-64 flex-col border-r border-line bg-charcoal px-5 py-7 lg:flex">
        <Brand />
        <div className="mt-14 grid gap-2">
          <Button variant="quiet" className="justify-start rounded-xl bg-paper/8 px-4">
            <Icon name="grid" /> Visão geral
          </Button>
          <Button variant="ghost" className="justify-start rounded-xl px-4">
            <Icon name="calendar" /> Agenda
            <span className="ml-auto rounded-full bg-ember px-2 py-0.5 text-xs text-ink">3</span>
          </Button>
          <Button variant="ghost" className="justify-start rounded-xl px-4">
            <Icon name="list" /> Projetos
          </Button>
        </div>
        <div className="relative mt-auto mb-5 h-40 overflow-hidden rounded-3xl border border-ember/20 bg-ember/5 text-ember">
          <img
            src={new URL("./imports/download4-2.jfif", import.meta.url).href}
            alt=""
            className="absolute inset-0 h-full w-full scale-110 object-cover object-center opacity-25 invert mix-blend-screen"
          />
          <div className="absolute bottom-4 left-4 z-10 text-xs font-bold uppercase tracking-[0.22em] text-copper">
            Desde 2018
          </div>
        </div>
        <div className="border-t border-line pt-5">
          <div className="flex items-center gap-3 rounded-2xl bg-paper/5 p-3">
            <div className="grid size-10 place-items-center rounded-full bg-ember text-xs font-bold text-ink">VS</div>
            <div className="min-w-0">
              <div className="truncate text-sm font-semibold">Vitor Sales</div>
              <div className="text-xs text-smoke">Tatuador</div>
            </div>
            <Icon name="chevron" className="ml-auto size-4 text-smoke" />
          </div>
        </div>
      </aside>

      <main className="relative z-10 lg:ml-64">
        <div className="mx-auto max-w-screen-2xl px-5 py-8 sm:px-8 lg:px-10 lg:py-10">
          <div className="tattoo-hero relative overflow-hidden rounded-3xl border border-ember/20 px-6 py-8 sm:px-9 sm:py-10 xl:flex xl:items-end xl:justify-between">
            <img
              src={new URL("./imports/download4-1.jfif", import.meta.url).href}
              alt=""
              className="pointer-events-none absolute inset-0 h-full w-full scale-110 object-contain object-center opacity-20 invert mix-blend-screen"
            />
            <div className="relative z-10 max-w-3xl px-4 py-3">
              <CornerOrnaments className="-inset-3 opacity-60" />
              <div className="mb-3 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.22em] text-ember">
                <Icon name="spark" className="size-4" /> Quarta, 12 de junho
              </div>
              <div className="font-display text-5xl leading-none sm:text-7xl">
                Arte viva,
                <span className="block italic text-ember">agenda em ordem.</span>
              </div>
              <div className="mt-5 max-w-xl text-smoke">Bom dia, Vitor. O estúdio está em movimento e três projetos pedem sua atenção hoje.</div>
            </div>
            <div className="relative z-10 mt-7 flex flex-wrap gap-3 px-4 py-3 xl:mt-0">
              <CornerOrnaments className="-inset-1 opacity-70" compact />
              <Button variant="outline"><Icon name="calendar" /> Ver agenda</Button>
              <Button onClick={() => setShowStep(true)}><Icon name="plus" /> Registrar passo</Button>
            </div>
          </div>

          <section className="grid gap-3 py-6 sm:grid-cols-3">
            {[
              ["03", "Ações pendentes", "Precisam de você", "text-ember", "eye"],
              ["02", "Sessões hoje", "Próxima às 14h", "text-sage", "dagger"],
              ["08", "Projetos ativos", "+2 este mês", "text-copper", "rose"],
            ].map(([number, label, detail, color, art]) => (
              <div key={label} className="group relative overflow-hidden rounded-2xl border border-line bg-charcoal p-5 transition hover:-translate-y-1 hover:border-ember/40">
                <FlashArt name={art as FlashName} className={`absolute -right-4 -top-4 size-24 opacity-10 transition group-hover:rotate-6 group-hover:opacity-25 ${color}`} />
                <div className={`relative font-display text-4xl ${color}`}>{number}</div>
                <div className="relative mt-2 text-sm font-semibold">{label}</div>
                <div className="relative mt-1 text-xs text-smoke">{detail}</div>
              </div>
            ))}
          </section>

          <div className="grid gap-6 xl:grid-cols-5">
            <section className="min-w-0 xl:col-span-3">
              <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="font-display text-3xl">Projetos</div>
                  <div className="mt-1 text-sm text-smoke">Acompanhe cada história, do traço ao retoque.</div>
                </div>
                <div className="flex items-center gap-2 overflow-x-auto pb-1">
                  {filters.map((item) => (
                    <Button
                      key={item}
                      variant={filter === item ? "primary" : "ghost"}
                      className="shrink-0 px-4 py-2 text-xs"
                      onClick={() => setFilter(item)}
                    >
                      {item}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="grid gap-3">
                {visible.map((tattoo) => (
                  <NativeButton
                    key={tattoo.id}
                    onClick={() => setSelectedId(tattoo.id)}
                    className={`group grid w-full gap-4 rounded-2xl border p-4 text-left transition sm:grid-cols-[auto_1fr_auto] sm:items-center ${selectedId === tattoo.id ? "border-ember/60 bg-charcoal" : "border-line bg-charcoal/60 hover:border-smoke/40 hover:bg-charcoal"}`}
                  >
                    <div className={`grid size-12 place-items-center rounded-xl ${tattoo.accent} font-display text-xl text-cream`}>{tattoo.initials}</div>
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="truncate font-semibold">{tattoo.title}</span>
                        <span className="text-xs text-smoke">#{String(tattoo.id).padStart(3, "0")}</span>
                      </div>
                      <div className="mt-1 text-sm text-smoke">{tattoo.client} · {tattoo.placement}</div>
                    </div>
                    <div className="flex items-center gap-3 sm:justify-end">
                      <StagePill stage={tattoo.stage} />
                      <Icon name="chevron" className="size-4 text-smoke transition group-hover:translate-x-1 group-hover:text-cream" />
                    </div>
                  </NativeButton>
                ))}
                {visible.length === 0 && (
                  <div className="rounded-2xl border border-dashed border-line p-10 text-center text-sm text-smoke">Nenhum projeto nesta etapa.</div>
                )}
              </div>
            </section>

            <aside className="h-fit overflow-hidden rounded-3xl border border-line bg-cream text-ink xl:sticky xl:top-8 xl:col-span-2">
              <div className="relative h-44 overflow-hidden">
                <img
                  src="https://images.unsplash.com/photo-1565058379802-bbe93b2f703a?auto=format&fit=crop&w=900&q=85"
                  alt="Tatuador trabalhando em um desenho no braço"
                  className="h-full w-full object-cover grayscale"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-ink/70 to-transparent" />
                <FlashArt name="rose" className="absolute -right-6 -top-8 size-40 text-cream opacity-30" />
                <div className="absolute bottom-4 left-5 right-5 flex items-end justify-between text-cream">
                  <div>
                    <div className="text-xs uppercase tracking-[0.2em] text-sand">Projeto #{String(selected.id).padStart(3, "0")}</div>
                    <div className="mt-1 font-display text-3xl">{selected.title}</div>
                  </div>
                  <div className="grid size-10 place-items-center rounded-full bg-ember font-bold text-ink">{selected.initials}</div>
                </div>
              </div>
              <div className="relative overflow-hidden p-5">
                <img
                  src={new URL("./imports/download3-1.jfif", import.meta.url).href}
                  alt=""
                  className="absolute -left-4 inset-y-0 h-full w-1/3 object-contain object-left opacity-15 mix-blend-multiply"
                />
                <img
                  src={new URL("./imports/download3-1.jfif", import.meta.url).href}
                  alt=""
                  className="absolute -right-4 inset-y-0 h-full w-1/3 -scale-x-100 object-contain object-left opacity-15 mix-blend-multiply"
                />
                <img
                  src={new URL("./imports/download5.jfif", import.meta.url).href}
                  alt=""
                  className="absolute inset-0 h-full w-full scale-120 object-contain object-center p-8 opacity-20 mix-blend-multiply"
                />
                <div className="relative flex items-center justify-between gap-4">
                  <div>
                    <div className="text-sm font-semibold">{selected.client}</div>
                    <div className="mt-1 text-xs text-stone">{selected.placement} · {selected.size}</div>
                  </div>
                  <StagePill stage={selected.stage} />
                </div>

                <div className="relative my-5 h-px bg-ink/10" />
                <div className="relative text-xs font-bold uppercase tracking-[0.18em] text-stone">Linha do tempo</div>
                <div className="relative mt-5 grid gap-0">
                  {[
                    ["Pedido recebido", "28 Mai", true],
                    ["Desenho aprovado", "04 Jun", selected.stage !== "Pedida"],
                    ["Primeira sessão", "10 Jun", selected.stage === "Em sessões" || selected.stage === "Finalizada"],
                    ["Retoque", "Após cicatrização", selected.stage === "Finalizada"],
                  ].map(([label, date, done], index) => (
                    <div key={String(label)} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div className={`grid size-6 place-items-center rounded-full border ${done ? "border-olive bg-olive text-cream" : "border-ink/20 bg-cream text-stone"}`}>
                          {done ? <Icon name="check" className="size-3" /> : <span className="size-1 rounded-full bg-stone" />}
                        </div>
                        {index < 3 && <div className="h-10 w-px bg-ink/15" />}
                      </div>
                      <div className="flex-1">
                        <div className={`text-sm font-semibold ${done ? "text-ink" : "text-stone"}`}>{label}</div>
                        <div className="mt-0.5 text-xs text-stone">{date}</div>
                      </div>
                    </div>
                  ))}
                </div>
                <Button className="relative mt-5 w-full" onClick={() => setShowStep(true)}>
                  Registrar próximo passo <Icon name="arrow" />
                </Button>
              </div>
            </aside>
          </div>
        </div>
      </main>

      {saved && (
        <div className="fixed bottom-5 right-5 z-50 flex items-center gap-3 rounded-2xl border border-sage/30 bg-olive px-5 py-4 text-sm font-semibold text-cream shadow-2xl">
          <Icon name="check" /> Passo registrado e etapa atualizada.
        </div>
      )}

      {showStep && (
        <div className="fixed inset-0 z-50 grid place-items-end bg-ink/80 p-0 backdrop-blur-sm sm:place-items-center sm:p-5">
          <form onSubmit={saveStep} className="w-full max-w-lg rounded-t-3xl border border-line bg-charcoal p-6 shadow-2xl sm:rounded-3xl sm:p-8">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.2em] text-ember">Atualizar projeto</div>
                <div className="mt-2 font-display text-4xl">{selected.title}</div>
                <div className="mt-2 text-sm text-smoke">Registre o que foi feito. A etapa muda automaticamente.</div>
              </div>
              <Button type="button" variant="ghost" className="size-10 px-0 text-xl" onClick={() => setShowStep(false)}>×</Button>
            </div>
            <div className="mt-7 grid gap-5">
              <Field label="Tipo de passo">
                <NativeSelect name="step" className="field-control" defaultValue={selected.stage === "Pedida" ? "Desenho aprovado" : "Sessão"}>
                  <option>Desenho aprovado</option>
                  <option>Sessão</option>
                  <option>Retoque</option>
                </NativeSelect>
              </Field>
              <Field label="Data">
                <NativeInput name="date" type="date" defaultValue="2025-06-12" className="field-control" />
              </Field>
              <Field label="Observação" hint="Opcional, mas ajuda a manter o histórico completo.">
                <NativeTextarea name="note" rows={3} className="field-control resize-none" placeholder="Ex.: Finalizamos linhas e iniciamos sombreamento..." />
              </Field>
            </div>
            <div className="mt-7 flex gap-3">
              <Button type="button" variant="outline" className="flex-1" onClick={() => setShowStep(false)}>Cancelar</Button>
              <Button type="submit" className="flex-1">Salvar passo</Button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

function ClientApp() {
  const [tab, setTab] = useState<"tattoos" | "request">("tattoos");
  const [sent, setSent] = useState(false);

  function sendRequest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSent(true);
  }

  return (
    <div className="min-h-screen bg-cream text-ink">
      <InkBackdrop light />
      <header className="sticky top-0 z-30 border-b border-ink/10 bg-cream/90 backdrop-blur-xl">
        <div className="relative mx-auto flex h-20 max-w-6xl items-center justify-between overflow-hidden px-5">
          <div className="relative z-10"><Brand light /></div>
          <img
            src={new URL("./imports/download-1.jfif", import.meta.url).href}
            alt=""
            className="pointer-events-none absolute left-1/2 top-0 h-120 w-60 -translate-x-1/2 -translate-y-1/2 -rotate-90 object-contain opacity-15 mix-blend-multiply"
          />
          <div className="relative z-10 flex items-center gap-3">
            <span className="hidden text-sm sm:block">Olá, Bruna</span>
            <div className="grid size-10 place-items-center rounded-full bg-plum text-sm font-bold text-cream">BM</div>
          </div>
        </div>
      </header>
      <main className="relative z-10 mx-auto max-w-6xl px-5 pb-28 pt-9 sm:px-8 sm:pt-14">
        {tab === "tattoos" && (
          <>
            <div className="client-hero relative overflow-hidden rounded-3xl bg-rust px-6 py-9 text-cream sm:px-10 sm:py-12">
              <img
                src={new URL("./imports/download4-1.jfif", import.meta.url).href}
                alt=""
                className="pointer-events-none absolute inset-0 h-full w-full scale-110 object-contain object-center opacity-20 invert mix-blend-screen"
              />
              <div className="relative z-10 max-w-2xl px-5 py-4">
                <CornerOrnaments className="-inset-2 text-sand opacity-70" />
                <div className="text-xs font-bold uppercase tracking-[0.2em] text-sand">Sua jornada na pele</div>
                <div className="mt-2 font-display text-5xl sm:text-7xl">Histórias que ficam.</div>
                <div className="mt-4 max-w-lg text-cream/70">Acompanhe cada traço, cada sessão e tudo o que vem depois.</div>
                <div className="relative mt-7 inline-flex px-3 py-2">
                  <CornerOrnaments className="-inset-1 text-sand opacity-80" compact />
                  <Button onClick={() => setTab("request")}><Icon name="plus" /> Pedir tatuagem</Button>
                </div>
              </div>
            </div>

            <div className="mt-10 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <div className="overflow-hidden rounded-3xl bg-ink text-cream">
                <div className="relative h-56">
                  <img
                    src="https://images.unsplash.com/photo-1567071208639-716c1009517d?auto=format&fit=crop&w=1000&q=85"
                    alt="Detalhe de tatuagem floral sendo feita"
                    className="h-full w-full object-cover grayscale"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/20 to-transparent" />
                  <div className="absolute right-5 top-5 rounded-full border border-cream/30 bg-ink/40 px-3 py-1 text-xs uppercase tracking-[0.2em] backdrop-blur">Em processo</div>
                  <div className="absolute bottom-5 left-5 right-5">
                    <StagePill stage="Em sessões" />
                    <div className="mt-3 font-display text-4xl">Jardim botânico</div>
                  </div>
                </div>
                <div className="p-5 sm:p-7">
                  <div className="grid grid-cols-2 gap-5 border-b border-line pb-6">
                    <div><div className="text-xs text-smoke">Local</div><div className="mt-1 text-sm font-semibold">Costela esquerda</div></div>
                    <div><div className="text-xs text-smoke">Tamanho</div><div className="mt-1 text-sm font-semibold">28 cm</div></div>
                  </div>
                  <div className="mt-6 flex items-center gap-3 rounded-2xl bg-paper/6 p-4">
                    <div className="grid size-10 place-items-center rounded-full bg-ember text-ink"><Icon name="calendar" /></div>
                    <div>
                      <div className="text-xs text-smoke">Próximo passo</div>
                      <div className="mt-1 text-sm font-semibold">Sessão 02 · 18 Jun, 14h</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="relative overflow-hidden rounded-3xl border border-ink/10 bg-paper p-6 sm:p-8">
                <img
                  src={new URL("./imports/download3-1.jfif", import.meta.url).href}
                  alt=""
                  className="absolute -left-4 inset-y-0 h-full w-1/3 object-contain object-left opacity-10 mix-blend-multiply"
                />
                <img
                  src={new URL("./imports/download3-1.jfif", import.meta.url).href}
                  alt=""
                  className="absolute -right-4 inset-y-0 h-full w-1/3 -scale-x-100 object-contain object-left opacity-10 mix-blend-multiply"
                />
                <img
                  src={new URL("./imports/download5.jfif", import.meta.url).href}
                  alt=""
                  className="absolute inset-0 h-full w-full scale-120 object-contain object-center p-8 opacity-15 mix-blend-multiply"
                />
                <div className="relative flex items-center justify-between">
                  <div>
                    <div className="text-xs font-bold uppercase tracking-[0.18em] text-rust">Histórico</div>
                    <div className="mt-2 font-display text-3xl">Seu caminho até aqui</div>
                  </div>
                  <Icon name="spark" className="size-6 text-rust" />
                </div>
                <div className="relative mt-8">
                  {[
                    ["Pedido recebido", "28 de maio", "Sua ideia chegou ao estúdio."],
                    ["Desenho aprovado", "04 de junho", "Arte final aprovada por você."],
                    ["Primeira sessão", "10 de junho", "Linhas finalizadas. Cicatrização ótima."],
                    ["Segunda sessão", "18 de junho", "Próximo passo"],
                  ].map(([title, date, detail], index) => (
                    <div key={title} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div className={`grid size-7 place-items-center rounded-full ${index < 3 ? "bg-olive text-cream" : "border border-rust bg-cream text-rust"}`}>
                          {index < 3 ? <Icon name="check" className="size-3.5" /> : <span className="size-1.5 rounded-full bg-rust" />}
                        </div>
                        {index < 3 && <div className="h-16 w-px bg-ink/15" />}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-baseline justify-between gap-3">
                          <span className="text-sm font-semibold">{title}</span>
                          <span className="text-xs text-stone">{date}</span>
                        </div>
                        <div className="mt-1 text-xs text-stone">{detail}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}

        {tab === "request" && (
          <div className="mx-auto max-w-3xl">
            {!sent ? (
              <>
                <Button variant="ghost" className="-ml-4 text-stone hover:bg-ink/5 hover:text-ink" onClick={() => setTab("tattoos")}>← Voltar</Button>
                <div className="mt-5 text-xs font-bold uppercase tracking-[0.2em] text-rust">Um novo projeto</div>
                <div className="mt-2 font-display text-5xl sm:text-6xl">Conte sua ideia.</div>
                <div className="mt-4 max-w-xl text-stone">Não precisa saber explicar tudo. Dê os primeiros detalhes e construímos o desenho com você.</div>
                <form onSubmit={sendRequest} className="mt-9 grid gap-6 rounded-3xl border border-ink/10 bg-paper p-5 sm:p-8">
                  <Field label="O que você imagina?" light>
                    <NativeTextarea required rows={5} className="field-control field-light resize-none" placeholder="Ex.: Um jardim com flores brasileiras e uma mariposa ao centro..." />
                  </Field>
                  <div className="grid gap-5 sm:grid-cols-2">
                    <Field label="Local do corpo" light>
                      <NativeInput required className="field-control field-light" placeholder="Ex.: Costela esquerda" />
                    </Field>
                    <Field label="Tamanho aproximado" light>
                      <NativeSelect className="field-control field-light" defaultValue="">
                        <option value="" disabled>Selecione</option>
                        <option>Pequena · até 10 cm</option>
                        <option>Média · 10 a 20 cm</option>
                        <option>Grande · mais de 20 cm</option>
                      </NativeSelect>
                    </Field>
                  </div>
                  <div className="flex flex-col-reverse gap-3 border-t border-ink/10 pt-6 sm:flex-row sm:items-center sm:justify-between">
                    <span className="text-xs text-stone">Você poderá ajustar tudo antes de aprovar o desenho.</span>
                    <Button type="submit">Enviar pedido <Icon name="arrow" /></Button>
                  </div>
                </form>
              </>
            ) : (
              <div className="rounded-3xl bg-ink p-8 text-center text-cream sm:p-14">
                <div className="mx-auto grid size-16 place-items-center rounded-full bg-olive"><Icon name="check" className="size-7" /></div>
                <div className="mt-7 font-display text-5xl">Ideia recebida.</div>
                <div className="mx-auto mt-4 max-w-md text-sm leading-6 text-smoke">Seu projeto já entrou no nosso caderno. O Vitor vai revisar o briefing e preparar os próximos passos.</div>
                <Button className="mt-8" onClick={() => { setSent(false); setTab("tattoos"); }}>Ver minhas tatuagens</Button>
              </div>
            )}
          </div>
        )}
      </main>
      <nav className="fixed inset-x-0 bottom-0 z-30 border-t border-ink/10 bg-cream/95 p-3 backdrop-blur-xl sm:hidden">
        <div className="grid grid-cols-2 gap-2">
          <Button variant={tab === "tattoos" ? "primary" : "ghost"} className={tab === "tattoos" ? "" : "text-stone hover:bg-ink/5 hover:text-ink"} onClick={() => setTab("tattoos")}><Icon name="list" /> Meus projetos</Button>
          <Button variant={tab === "request" ? "primary" : "ghost"} className={tab === "request" ? "" : "text-stone hover:bg-ink/5 hover:text-ink"} onClick={() => { setSent(false); setTab("request"); }}><Icon name="plus" /> Novo pedido</Button>
        </div>
      </nav>
    </div>
  );
}

export default function App() {
  const [mode, setMode] = useState<"artist" | "client">("artist");

  return (
    <>
      <div className="fixed right-5 top-24 z-40 flex rounded-full border border-line bg-charcoal/95 p-1 shadow-2xl backdrop-blur-xl lg:top-5">
        <Button variant={mode === "artist" ? "primary" : "ghost"} className="px-4 py-2 text-xs" onClick={() => setMode("artist")}>
          <Icon name="ink" className="size-4" /> Ateliê
        </Button>
        <Button variant={mode === "client" ? "primary" : "ghost"} className="px-4 py-2 text-xs" onClick={() => setMode("client")}>
          <Icon name="user" className="size-4" /> Minha área
        </Button>
      </div>
      {mode === "artist" ? <ArtistApp /> : <ClientApp />}
    </>
  );
}
