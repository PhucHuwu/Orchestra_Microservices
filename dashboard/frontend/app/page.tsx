const cards = [
  "Playback Control",
  "Realtime Tempo",
  "System Monitoring",
  "Fault Demo",
];

export default function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-8 md:px-8">
      <h1 className="text-4xl font-semibold">Orchestra Dashboard Skeleton</h1>
      <p className="mt-2 text-lg">Baseline UI for control and observability screens.</p>

      <section className="mt-8 grid gap-4 md:grid-cols-2">
        {cards.map((card) => (
          <article
            key={card}
            className="rounded-xl border border-black/10 bg-[var(--card)] p-5 shadow-sm"
          >
            <h2 className="text-2xl">{card}</h2>
            <p className="mt-2 text-sm opacity-80">Placeholder widget and route to be implemented.</p>
          </article>
        ))}
      </section>
    </main>
  );
}
