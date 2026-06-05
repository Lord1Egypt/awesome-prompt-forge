export interface PromptMeta {
  name: string;
  category: string;
  description: string;
  path: string;
}

export declare class Prompt {
  name: string;
  category: string;
  description: string;
  path: string;
  content: string;
  toString(): string;
}

export declare function load(name: string, category?: string): Prompt;
export declare function search(
  query: string,
  category?: string,
  limit?: number
): PromptMeta[];
export declare function listPrompts(category?: string): PromptMeta[];
export declare function categories(): Record<string, number>;
