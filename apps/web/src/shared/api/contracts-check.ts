import type { components } from "@country-decision-atlas/contracts/generated/types";

type CountryListResponse = components["schemas"]["CountryListResponse"];
type CountryResponse = components["schemas"]["CountryResponse"];
type CountryReadModelResponse = components["schemas"]["CountryReadModelResponse"];
type DecisionRunRequest = components["schemas"]["DecisionRunRequest"];
type DecisionRunResponse = components["schemas"]["DecisionRunResponse"];
type LegalSignalListResponse = components["schemas"]["LegalSignalDetailListResponse"];
type SourceListResponse = components["schemas"]["SourceListResponse"];
type EvidenceItemListResponse = components["schemas"]["EvidenceItemListResponse"];
type ScenarioListResponse = components["schemas"]["ScenarioListResponse"];
type UserStoryListResponse = components["schemas"]["UserStoryListResponse"];
type DataQualityReport = components["schemas"]["DataQualityReport"];
type LocaleResolution = components["schemas"]["LocaleResolution"];
type ErrorResponse = components["schemas"]["ErrorResponse"];
type LocalizationMeta = components["schemas"]["LocalizationMeta"];
type TranslationFieldMeta = components["schemas"]["TranslationFieldMeta"];

export type FrontendCriticalContracts = {
  countryList: CountryListResponse;
  countryDetail: CountryResponse;
  countryReadModel: CountryReadModelResponse;
  decisionRunRequest: DecisionRunRequest;
  decisionRunResponse: DecisionRunResponse;
  legalSignals: LegalSignalListResponse;
  sources: SourceListResponse;
  evidenceItems: EvidenceItemListResponse;
  scenarios: ScenarioListResponse;
  userStories: UserStoryListResponse;
  dataQualityReport: DataQualityReport;
  locale: LocaleResolution;
  error: ErrorResponse;
  localizationMeta: LocalizationMeta;
  translationFieldMeta: TranslationFieldMeta;
};
