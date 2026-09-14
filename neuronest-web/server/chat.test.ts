import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";
import { NATURE_QUESTION_COUNT, findNatureAnswer } from "@shared/natureKnowledge";

function createContext(): TrpcContext {
  return {
    user: null,
    req: { protocol: "https", headers: {} } as TrpcContext["req"],
    res: {} as TrpcContext["res"],
  };
}

describe("NeuroNest curated nature chat", () => {
  it("ships at least 200 reviewed questions", () => {
    expect(NATURE_QUESTION_COUNT).toBeGreaterThanOrEqual(6500);
  });

  it("answers a known question from curated knowledge without model fallback", async () => {
    const caller = appRouter.createCaller(createContext());
    const result = await caller.chat.ask({ message: "What is biodiversity?" });

    expect(result.source).toBe("curated_nature_knowledge");
    expect(result.confidence).toBe(1);
    expect(result.matchedQuestion).toBe("What is biodiversity?");
    expect(result.response).toContain("variety of life");
    expect(result.questionCount).toBe(NATURE_QUESTION_COUNT);
  });

  it("accepts a punctuation-tolerant known question", () => {
    const result = findNatureAnswer("WHAT IS PHOTOSYNTHESIS");
    expect(result?.confidence).toBe(1);
    expect(result?.entry.question).toBe("What is photosynthesis?");
  });

  it("answers a question from the imported 1,000-question set", async () => {
    const caller = appRouter.createCaller(createContext());
    const result = await caller.chat.ask({ message: "How can removing a keystone species cause changes across several trophic levels?" });

    expect(result.source).toBe("curated_nature_knowledge");
    expect(result.confidence).toBe(1);
    expect(result.response).toContain("Changes propagate");
  });

  it("answers a question from the imported Parquet learning corpus", async () => {
    const caller = appRouter.createCaller(createContext());
    const result = await caller.chat.ask({ message: "What is pairwise distance computation?" });

    expect(result.source).toBe("curated_nature_knowledge");
    expect(result.confidence).toBe(1);
    expect(result.response).toContain("evolutionary distance");
  });
});
