import { Link } from "react-router-dom";
import { Flask, Lightning, Atom, Gauge, ChartLine, BatteryCharging, ArrowUpRight } from "@phosphor-icons/react";

const ICONS = {
  flask: Flask,
  lightning: Lightning,
  atom: Atom,
  gauge: Gauge,
  "chart-line": ChartLine,
  "battery-charging": BatteryCharging,
};

export default function TopicCard({ topic, index }) {
  const Icon = ICONS[topic.icon] || Flask;
  const num = String(index + 1).padStart(2, "0");

  return (
    <Link
      to={`/topico/${topic.id}`}
      data-testid={`topic-card-${topic.slug}`}
      className="block border border-[#E0E2DB] bg-white p-6 hard-shadow-hover group"
    >
      <div className="flex items-start justify-between mb-6">
        <div className="font-mono text-[10px] uppercase tracking-[0.25em] text-[#5C5F66]">
          Módulo · {topic.module}
        </div>
        <span className="font-mono text-xs text-[#5C5F66]">/{num}</span>
      </div>

      <div className="w-12 h-12 border border-[#0F1115] bg-[#F4F5F2] flex items-center justify-center mb-5">
        <Icon size={24} weight="duotone" />
      </div>

      <h3 className="font-display font-bold text-xl leading-tight mb-3 group-hover:text-[#0022FF] transition-colors">
        {topic.title}
      </h3>
      <p className="text-sm text-[#5C5F66] leading-relaxed mb-6 line-clamp-3">
        {topic.description}
      </p>

      <div className="flex items-center justify-between pt-4 border-t border-[#E0E2DB]">
        <span className="font-mono text-[10px] uppercase tracking-[0.2em]">
          Iniciar estudo
        </span>
        <ArrowUpRight size={18} weight="bold" className="group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
      </div>
    </Link>
  );
}
