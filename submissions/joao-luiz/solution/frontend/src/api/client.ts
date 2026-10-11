/** Fetches the current view and keeps role + filter. A change refetches the queue. */

export type Role = "seller" | "manager";

export type ViewFilter = {
  agent?: string;
  manager?: string;
  office?: string;
};

export type QueueItem = {
  opportunity_id: string;
  product: string;
  account: string;
  value: number;
  deal_stage: string;
  age_days: number;
  score: number;
  estado: string;
  confidence: string;
  reason: string;
  action: string;
  from_agent?: string | null;
};

export type ReviewItem = {
  opportunity_id: string;
  product: string;
  account: string | null;
  deal_stage: string;
  value: number;
  age_days: number | null;
  estado: string;
  reason: string;
  action: string;
};

export type QueueResponse = {
  view: string | null;
  items: QueueItem[];
  trabalhar?: QueueItem[];
  decidir?: QueueItem[];
  revisar: ReviewItem[];
  empty_message: string | null;
};

export type RollupRow = {
  sales_agent: string;
  queued_count: number;
  expected_value_sum: number;
  cooling_count: number;
  good_deals_cooling: number;
  trabalhar_count?: number;
  trabalhar_value?: number;
  decidir_count?: number;
  decidir_value?: number;
};

export type RollupResponse = {
  rows: RollupRow[];
  parked_value?: number;
};

export type AgentOption = {
  sales_agent: string;
  manager: string | null;
  regional_office: string | null;
  deal_count: number;
  empty: boolean;
};

export type AgentsResponse = {
  agents: AgentOption[];
  managers: string[];
  offices: string[];
};

export type HandoffResponse = {
  opportunity_id: string;
  sales_agent: string;
  from_agent: string;
};

export async function postHandoff(input: {
  opportunity_id: string;
  to_agent: string;
}): Promise<HandoffResponse> {
  const response = await fetch("/api/handoff", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      opportunity_id: input.opportunity_id,
      to_agent: input.to_agent,
    }),
  });
  if (!response.ok) {
    throw new Error(await errorDetail(response));
  }
  return response.json() as Promise<HandoffResponse>;
}

export async function fetchHandoffCandidates(opportunityId: string): Promise<string[]> {
  const path = withParams("/api/handoff/candidates", { opportunity_id: opportunityId });
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(await errorDetail(response));
  }
  const body = (await response.json()) as { candidates: string[] };
  return body.candidates;
}

async function errorDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail) {
      return body.detail;
    }
  } catch {
    // The status is the fallback when the body is not the spec detail.
  }
  return `request failed: ${response.status}`;
}

export type ViewSnapshot = {
  role: Role;
  filter: ViewFilter;
  queue: QueueResponse;
  rollup: RollupResponse;
  agents: AgentsResponse;
};

const VIEW_PARAM: Record<Role, "mine" | "team"> = {
  seller: "mine",
  manager: "team",
};

export function createViewClient(baseUrl = "") {
  let role: Role = "seller";
  let filter: ViewFilter = {};
  let snapshot: ViewSnapshot | null = null;

  async function read<T>(path: string): Promise<T> {
    const response = await fetch(`${baseUrl}${path}`);
    if (!response.ok) {
      throw new Error(`GET ${path} failed: ${response.status}`);
    }
    return response.json() as Promise<T>;
  }

  async function refresh(): Promise<ViewSnapshot> {
    const [queue, rollup, agents] = await Promise.all([
      read<QueueResponse>(queuePath(role, filter)),
      read<RollupResponse>(rollupPath(filter)),
      read<AgentsResponse>("/api/agents"),
    ]);
    snapshot = { role, filter: { ...filter }, queue, rollup, agents };
    return snapshot;
  }

  return {
    getState(): ViewSnapshot | null {
      return snapshot;
    },
    load: refresh,
    async setRole(next: Role): Promise<ViewSnapshot> {
      role = next;
      return refresh();
    },
    async setFilter(next: ViewFilter): Promise<ViewSnapshot> {
      filter = { ...next };
      return refresh();
    },
  };
}

export function queuePath(role: Role, filter: ViewFilter): string {
  return withParams("/api/queue", {
    view: VIEW_PARAM[role],
    agent: filter.agent,
    manager: filter.manager,
    office: filter.office,
  });
}

export function rollupPath(filter: ViewFilter): string {
  return withParams("/api/rollup", {
    manager: filter.manager,
    office: filter.office,
  });
}

function withParams(path: string, params: Record<string, string | undefined>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value) {
      search.set(key, value);
    }
  }
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}
