import type { QuestionVariant } from "@/types/enums";
import type { RawQueryJson } from "@/types/query";

export class QueryManager {
  private queries: RawQueryJson[] = [];

  constructor() {}

  public loadFromJson(data: RawQueryJson[]): void {
    this.queries = data;
  }

  public flatten(): Record<QuestionVariant, string>[] {
    return this.queries.map(query => {
      // Wir extrahieren nur die text_variants und ignorieren Metadaten wie IDs
      return { ...query.text_variants };
    });
  }

  public getAllQueries(): RawQueryJson[] {
    return this.queries;
  }
}