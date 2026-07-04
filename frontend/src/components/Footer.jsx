export default function Footer() {
  return (
    <footer className="border-t border-[#E0E2DB] mt-24" data-testid="site-footer">
      <div className="max-w-7xl mx-auto px-6 lg:px-10 py-10 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="md:col-span-2">
          <div className="font-display font-bold text-lg">
            Estúdio<span className="text-[#0022FF]">.</span>Química
          </div>
          <p className="text-sm text-[#5C5F66] mt-2 max-w-md">
            Plataforma de estudos focada em química para o ensino médio e pré-vestibular.
            Conteúdo, resumos gerados por IA, exercícios e vídeos.
          </p>
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#5C5F66] mb-2">
            Módulos
          </div>
          <ul className="space-y-1 text-sm">
            <li>Cinética Química</li>
            <li>Eletroquímica</li>
          </ul>
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#5C5F66] mb-2">
            Recursos
          </div>
          <ul className="space-y-1 text-sm">
            <li>Conteúdo teórico</li>
            <li>Resumos por IA</li>
            <li>Exercícios comentados</li>
            <li>Vídeoaulas</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-[#E0E2DB] py-4 text-center font-mono text-[10px] uppercase tracking-[0.2em] text-[#5C5F66]">
        © {new Date().getFullYear()} Estúdio Química · Feito para estudar de verdade
      </div>
    </footer>
  );
}
