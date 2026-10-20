import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { invokeLLM } from "./_core/llm";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router } from "./_core/trpc";
import { z } from "zod";
import { findNatureAnswer, NATURE_QUESTION_COUNT } from "@shared/natureKnowledge";

function extractText(content: unknown): string {
  if (typeof content === "string") return content.trim();
  if (Array.isArray(content)) {
    return content
      .map(part => (typeof part === "string" ? part : (part as { text?: string })?.text ?? ""))
      .join("\n")
      .trim();
  }
  return "";
}

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),
  chat: router({
    ask: publicProcedure
      .input(z.object({ message: z.string().trim().min(1).max(500) }))
      .mutation(async ({ input }) => {
        const curated = findNatureAnswer(input.message);
        if (curated) {
          return {
            response: curated.entry.answer,
            source: "curated_nature_knowledge" as const,
            confidence: Number(curated.confidence.toFixed(3)),
            matchedQuestion: curated.entry.question,
            questionCount: NATURE_QUESTION_COUNT,
          };
        }

        try {
          const completion = await invokeLLM({
            messages: [
              {
                role: "system",
                content:
                  "You are NeuroNest, a broad evolving AI companion and learning system. Nature is a major learning domain, not your entire identity. Answer clearly and briefly. Do not invent facts, sources, numbers, or memories. If you are uncertain, say so. Prefer explaining what is known and what would need verification.",
              },
              { role: "user", content: input.message },
            ],
          });
          const response = extractText(completion.choices?.[0]?.message?.content);
          if (response) {
            return {
              response,
              source: "hosted_llm" as const,
              confidence: null,
              matchedQuestion: null,
              questionCount: NATURE_QUESTION_COUNT,
            };
          }
        } catch (error) {
          console.warn("[NeuroNest] Hosted LLM unavailable:", error);
        }

        return {
          response:
            "I do not have a reviewed answer for that question yet. I can still help you explore the idea carefully through the hosted model, or you can start with one of the reviewed nature questions in the learning compass.",
          source: "safe_fallback" as const,
          confidence: null,
          matchedQuestion: null,
          questionCount: NATURE_QUESTION_COUNT,
        };
      }),
  }),
});

export type AppRouter = typeof appRouter;
