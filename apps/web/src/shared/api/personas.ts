import type { components } from "@country-decision-atlas/contracts/generated/types";

import { DEFAULT_LOCALE } from "../lib/locale";
import { apiGet, queryString } from "./http";

export type Persona = components["schemas"]["Persona"];
export type PersonaListResponse = components["schemas"]["PersonaListResponse"];
export type PersonaWeightProfileResponse =
  components["schemas"]["PersonaWeightProfileResponse"];

export function listPersonas(
  locale = DEFAULT_LOCALE,
): Promise<PersonaListResponse> {
  return apiGet<PersonaListResponse>(
    `/api/v1/personas${queryString({ locale })}`,
  );
}

export function getPersonaWeightProfile(
  personaSlug: string,
  scenarioSlug: string,
  locale = DEFAULT_LOCALE,
): Promise<PersonaWeightProfileResponse> {
  return apiGet<PersonaWeightProfileResponse>(
    `/api/v1/personas/${personaSlug}/weights${queryString({
      scenario: scenarioSlug,
      locale,
    })}`,
  );
}

export const personasApi = {
  listPersonas,
  getPersonaWeightProfile,
};
