import { Flame, Medal, Trophy, Star } from "@phosphor-icons/react";

/**
 * Computes badges based on progress and streak.
 * @param {Object} progress - {total, correct, accuracy, per_topic}
 * @param {Object} streak - {count, best}
 * @param {Array} topics - all topics
 * @returns {Array} badges [{id, label, desc, unlocked, icon}]
 */
export function computeBadges(progress, streak, topics) {
  const total = progress?.total || 0;
  const correct = progress?.correct || 0;
  const accuracy = progress?.accuracy || 0;
  const streakCount = streak?.count || 0;

  const modules = [...new Set((topics || []).map((t) => t.module))];
  const perTopic = progress?.per_topic || {};
  const masteredModules = modules.filter((m) => {
    const modTopics = topics.filter((t) => t.module === m);
    const stats = modTopics.reduce(
      (acc, t) => {
        const s = perTopic[t.id] || { total: 0, correct: 0 };
        acc.total += s.total; acc.correct += s.correct;
        return acc;
      },
      { total: 0, correct: 0 }
    );
    return stats.total >= 3 && stats.correct / stats.total >= 0.8;
  });

  return [
    { id: "first-blood", label: "Primeira Reação", desc: "Responder 1 exercício", icon: Star, unlocked: total >= 1 },
    { id: "quinteto", label: "Quinteto", desc: "Responder 5 exercícios", icon: Star, unlocked: total >= 5 },
    { id: "veterano", label: "Veterano", desc: "Responder 20 exercícios", icon: Medal, unlocked: total >= 20 },
    { id: "precisao-80", label: "Precisão 80%", desc: "Atingir 80% de acerto", icon: Trophy, unlocked: total >= 5 && accuracy >= 80 },
    { id: "streak-3", label: "Combustão", desc: "3 dias seguidos estudando", icon: Flame, unlocked: streakCount >= 3 },
    { id: "streak-7", label: "Reação em Cadeia", desc: "7 dias seguidos estudando", icon: Flame, unlocked: streakCount >= 7 },
    ...modules.map((m) => ({
      id: `master-${m}`,
      label: `Mestre em ${m.split(" ")[0]}`,
      desc: `80% de acerto em ${m}`,
      icon: Trophy,
      unlocked: masteredModules.includes(m),
    })),
  ];
}
