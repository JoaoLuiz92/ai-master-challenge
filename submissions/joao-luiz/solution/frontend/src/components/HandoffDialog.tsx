import { useEffect, useState } from "react";

import { fetchHandoffCandidates, postHandoff } from "../api/client";

const COOLING_AFTER_DAYS = 106;
const EMPTY_COPY = "Nenhum colega neste escritório";
const COOLING_COPY = "Este negócio está esfriando.";

export function HandoffDialog({
  opportunityId,
  ageDays,
  onConfirmed,
  onCancel,
}: {
  opportunityId: string;
  ageDays: number;
  onConfirmed: () => void;
  onCancel: () => void;
}) {
  const [candidates, setCandidates] = useState<string[] | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  useEffect(() => {
    let active = true;
    fetchHandoffCandidates(opportunityId)
      .then((names) => {
        if (active) {
          setCandidates(names);
        }
      })
      .catch((caught: unknown) => {
        if (!active) {
          return;
        }
        setCandidates([]);
        setError(caught instanceof Error ? caught.message : "request failed");
      });
    return () => {
      active = false;
    };
  }, [opportunityId]);

  async function confirm() {
    if (!selected || pending) {
      return;
    }
    setPending(true);
    setError(null);
    try {
      await postHandoff({ opportunity_id: opportunityId, to_agent: selected });
      onConfirmed();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "request failed");
      setPending(false);
    }
  }

  const names = candidates ?? [];
  const empty = candidates !== null && names.length === 0 && error === null;

  return (
    <dialog className="handoff-dialog" open role="dialog" aria-labelledby="handoff-title">
      <h2 id="handoff-title">Passar para colega</h2>
      {ageDays > COOLING_AFTER_DAYS ? <p className="handoff-note">{COOLING_COPY}</p> : null}
      {candidates === null ? <p>Carregando colegas</p> : null}
      {empty ? <p>{EMPTY_COPY}</p> : null}
      {names.length > 0 ? (
        <fieldset>
          <legend>Colega</legend>
          {names.map((name) => (
            <label key={name}>
              <input
                type="radio"
                name="colega"
                value={name}
                checked={selected === name}
                onChange={() => setSelected(name)}
              />
              {name}
            </label>
          ))}
        </fieldset>
      ) : null}
      {error ? <p role="alert">{error}</p> : null}
      <div className="handoff-actions">
        {names.length > 0 ? (
          <button type="button" onClick={() => void confirm()} disabled={!selected || pending}>
            Confirmar
          </button>
        ) : null}
        <button type="button" onClick={onCancel}>
          Cancelar
        </button>
      </div>
    </dialog>
  );
}
