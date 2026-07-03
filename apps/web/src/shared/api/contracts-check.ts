import type { components } from "@country-decision-atlas/contracts/generated/types";

type CiiCountryComparisonResponse =
  components["schemas"]["CiiCountryComparisonResponse"];
type CompareMatrixResponse = components["schemas"]["CompareMatrixResponse"];
type CountryListResponse = components["schemas"]["CountryListResponse"];
type CountryResponse = components["schemas"]["CountryResponse"];
type CountryReadModelResponse = components["schemas"]["CountryReadModelResponse"];
type DecisionRunRequest = components["schemas"]["DecisionRunRequest"];
type DecisionRunResponse = components["schemas"]["DecisionRunResponse"];
type DecisionPersonalizationResponse =
  components["schemas"]["DecisionPersonalizationResponse"];
type DecisionWeightItem = components["schemas"]["DecisionWeightItem"];
type DecisionWizardAnswers = components["schemas"]["DecisionWizardAnswers"];
type DecisionWizardRecommendation =
  components["schemas"]["DecisionWizardRecommendation"];
type LegalSignalListResponse = components["schemas"]["LegalSignalDetailListResponse"];
type LegalSignalTimelineResponse = components["schemas"]["LegalSignalTimelineResponse"];
type HomeOverviewResponse = components["schemas"]["HomeOverviewResponse"];
type RouteListResponse = components["schemas"]["RouteListResponse"];
type RouteDetailResponse = components["schemas"]["RouteDetailResponse"];
type RouteChecklistItem = components["schemas"]["RouteChecklistItem"];
type CountryPairCompatibilityResponse =
  components["schemas"]["CountryPairCompatibilityResponse"];
type CountryPairCompatibilityListResponse =
  components["schemas"]["CountryPairCompatibilityListResponse"];
type CountryPairCompatibilitySummary =
  components["schemas"]["CountryPairCompatibilitySummary"];
type DecisionPassportCreateRequest =
  components["schemas"]["DecisionPassportCreateRequest"];
type DecisionPassportCreateResponse =
  components["schemas"]["DecisionPassportCreateResponse"];
type DecisionPassportResponse = components["schemas"]["DecisionPassportResponse"];
type DecisionPassportMethodologySnapshot =
  components["schemas"]["DecisionPassportMethodologySnapshot"];
type DecisionPassportSourceRef = components["schemas"]["DecisionPassportSourceRef"];
type DecisionPassportRouteRef = components["schemas"]["DecisionPassportRouteRef"];
type WhatChangedItem = components["schemas"]["WhatChangedItem"];
type WhatChangedSummary = components["schemas"]["WhatChangedSummary"];
type WhatChangedResponse = components["schemas"]["WhatChangedResponse"];
type SourceListResponse = components["schemas"]["SourceListResponse"];
type EvidenceItemListResponse = components["schemas"]["EvidenceItemListResponse"];
type ScenarioListResponse = components["schemas"]["ScenarioListResponse"];
type UserStoryListResponse = components["schemas"]["UserStoryListResponse"];
type DataQualityReport = components["schemas"]["DataQualityReport"];
type LocaleResolution = components["schemas"]["LocaleResolution"];
type ErrorResponse = components["schemas"]["ErrorResponse"];
type LocalizationMeta = components["schemas"]["LocalizationMeta"];
type TranslationFieldMeta = components["schemas"]["TranslationFieldMeta"];
type Persona = components["schemas"]["Persona"];
type PersonaListResponse = components["schemas"]["PersonaListResponse"];
type PersonaWeightProfile = components["schemas"]["PersonaWeightProfile"];
type PersonaWeightProfileResponse =
  components["schemas"]["PersonaWeightProfileResponse"];
type AnalyticsEventCreate = components["schemas"]["AnalyticsEventCreate"];
type AnalyticsEventCreateResponse =
  components["schemas"]["AnalyticsEventCreateResponse"];
type FeatureFlag = components["schemas"]["FeatureFlag"];
type FeatureAccessRule = components["schemas"]["FeatureAccessRule"];
type FeatureAccessDecision = components["schemas"]["FeatureAccessDecision"];
type FeatureFlagListResponse = components["schemas"]["FeatureFlagListResponse"];
type FeatureFlagDetailResponse = components["schemas"]["FeatureFlagDetailResponse"];
type DataJournalEntry = components["schemas"]["DataJournalEntry"];
type CountryDataJournalResponse = components["schemas"]["CountryDataJournalResponse"];
type PlatformMetric = components["schemas"]["PlatformMetric"];
type PlatformMetricListResponse = components["schemas"]["PlatformMetricListResponse"];
type PlatformMetricsRecomputeSummary =
  components["schemas"]["PlatformMetricsRecomputeSummary"];
type CountryTrustResponse = components["schemas"]["CountryTrustResponse"];
type MethodologySection = components["schemas"]["MethodologySection"];
type MethodologyListResponse = components["schemas"]["MethodologyListResponse"];
type GlossaryTerm = components["schemas"]["GlossaryTerm"];
type GlossaryListResponse = components["schemas"]["GlossaryListResponse"];
type CountryDriftResponse = components["schemas"]["CountryDriftResponse"];
type CountryDriftSnapshot = components["schemas"]["CountryDriftSnapshot"];
type CountryDriftHistoryItem = components["schemas"]["CountryDriftHistoryItem"];
type CountryDriftRecomputeRequest =
  components["schemas"]["CountryDriftRecomputeRequest"];
type CountryDriftRecomputeResult = components["schemas"]["CountryDriftRecomputeResult"];
type CountryDriftBatchRecomputeResult =
  components["schemas"]["CountryDriftBatchRecomputeResult"];
type SearchResultItem = components["schemas"]["SearchResultItem"];
type SearchResponse = components["schemas"]["SearchResponse"];
type AIAskRequest = components["schemas"]["AIAskRequest"];
type AIAskResponse = components["schemas"]["AIAskResponse"];
type AIExplainNumberRequest = components["schemas"]["AIExplainNumberRequest"];
type AIExplainNumberResponse = components["schemas"]["AIExplainNumberResponse"];
type AIDecisionIntentRequest = components["schemas"]["AIDecisionIntentRequest"];
type AIDecisionIntentResponse = components["schemas"]["AIDecisionIntentResponse"];
type AICitation = components["schemas"]["AICitation"];
type AIProviderMeta = components["schemas"]["AIProviderMeta"];
type AIDraft = components["schemas"]["AIDraft"];
type AIDraftListResponse = components["schemas"]["AIDraftListResponse"];
type ContradictionCandidate = components["schemas"]["ContradictionCandidate"];
type ContradictionCandidateListResponse =
  components["schemas"]["ContradictionCandidateListResponse"];
type CommunityQuestion = components["schemas"]["CommunityQuestion"];
type CommunityQuestionListResponse =
  components["schemas"]["CommunityQuestionListResponse"];
type CommunityAnswer = components["schemas"]["CommunityAnswer"];
type ConsensusSummary = components["schemas"]["ConsensusSummary"];
type VoteSummary = components["schemas"]["VoteSummary"];
type DataErrorReport = components["schemas"]["DataErrorReport"];
type UserStoryRating = components["schemas"]["UserStoryRating"];
type AuthUser = components["schemas"]["AuthUser"];
type AuthSession = components["schemas"]["AuthSession"];
type AuthTokenResponse = components["schemas"]["AuthTokenResponse"];
type RegisterRequest = components["schemas"]["RegisterRequest"];
type LoginRequest = components["schemas"]["LoginRequest"];
type CurrentUserResponse = components["schemas"]["CurrentUserResponse"];
type UserSessionListResponse = components["schemas"]["UserSessionListResponse"];
type TelegramLinkRequest = components["schemas"]["TelegramLinkRequest"];
type TelegramLinkResponse = components["schemas"]["TelegramLinkResponse"];
type TelegramLinkStatusResponse = components["schemas"]["TelegramLinkStatusResponse"];
type WatchlistItem = components["schemas"]["WatchlistItem"];
type WatchlistResponse = components["schemas"]["WatchlistResponse"];
type WatchlistStatusResponse = components["schemas"]["WatchlistStatusResponse"];
type AdminUser = components["schemas"]["AdminUser"];
type AdminUserListResponse = components["schemas"]["AdminUserListResponse"];
type RoleUpdateRequest = components["schemas"]["RoleUpdateRequest"];
type UserStatusUpdateRequest = components["schemas"]["UserStatusUpdateRequest"];
type MigrationBoardPostListResponse =
  components["schemas"]["MigrationBoardPostListResponse"];
type MigrationBoardPostDetail = components["schemas"]["MigrationBoardPostDetail"];
type MyMigrationBoardPost = components["schemas"]["MyMigrationBoardPost"];
type MyMigrationBoardPostListResponse =
  components["schemas"]["MyMigrationBoardPostListResponse"];
type CreateMigrationBoardPostRequest =
  components["schemas"]["CreateMigrationBoardPostRequest"];
type UpdateMigrationBoardPostRequest =
  components["schemas"]["UpdateMigrationBoardPostRequest"];
type ContactRequestResponse = components["schemas"]["ContactRequestResponse"];
type ContactRequestListResponse = components["schemas"]["ContactRequestListResponse"];
type CompanionMatchesResponse = components["schemas"]["CompanionMatchesResponse"];
type MigrationBoardReportResponse =
  components["schemas"]["MigrationBoardReportResponse"];
type AdminMigrationBoardPostListResponse =
  components["schemas"]["AdminMigrationBoardPostListResponse"];

export type FrontendCriticalContracts = {
  ciiComparison: CiiCountryComparisonResponse;
  compareMatrix: CompareMatrixResponse;
  countryList: CountryListResponse;
  countryDetail: CountryResponse;
  countryReadModel: CountryReadModelResponse;
  decisionRunRequest: DecisionRunRequest;
  decisionRunResponse: DecisionRunResponse;
  decisionPersonalizationResponse: DecisionPersonalizationResponse;
  decisionWeightItem: DecisionWeightItem;
  decisionWizardAnswers: DecisionWizardAnswers;
  decisionWizardRecommendation: DecisionWizardRecommendation;
  legalSignals: LegalSignalListResponse;
  legalSignalTimeline: LegalSignalTimelineResponse;
  homeOverview: HomeOverviewResponse;
  routeList: RouteListResponse;
  routeDetail: RouteDetailResponse;
  routeChecklistItem: RouteChecklistItem;
  countryPairCompatibility: CountryPairCompatibilityResponse;
  countryPairCompatibilityList: CountryPairCompatibilityListResponse;
  countryPairCompatibilitySummary: CountryPairCompatibilitySummary;
  decisionPassportCreateRequest: DecisionPassportCreateRequest;
  decisionPassportCreateResponse: DecisionPassportCreateResponse;
  decisionPassportResponse: DecisionPassportResponse;
  decisionPassportMethodologySnapshot: DecisionPassportMethodologySnapshot;
  decisionPassportSourceRef: DecisionPassportSourceRef;
  decisionPassportRouteRef: DecisionPassportRouteRef;
  whatChangedItem: WhatChangedItem;
  whatChangedSummary: WhatChangedSummary;
  whatChangedResponse: WhatChangedResponse;
  sources: SourceListResponse;
  evidenceItems: EvidenceItemListResponse;
  scenarios: ScenarioListResponse;
  userStories: UserStoryListResponse;
  dataQualityReport: DataQualityReport;
  locale: LocaleResolution;
  error: ErrorResponse;
  localizationMeta: LocalizationMeta;
  translationFieldMeta: TranslationFieldMeta;
  persona: Persona;
  personas: PersonaListResponse;
  personaWeightProfile: PersonaWeightProfile;
  personaWeightProfileResponse: PersonaWeightProfileResponse;
  analyticsEventCreate: AnalyticsEventCreate;
  analyticsEventCreateResponse: AnalyticsEventCreateResponse;
  featureFlag: FeatureFlag;
  featureAccessRule: FeatureAccessRule;
  featureAccessDecision: FeatureAccessDecision;
  featureFlagListResponse: FeatureFlagListResponse;
  featureFlagDetailResponse: FeatureFlagDetailResponse;
  dataJournalEntry: DataJournalEntry;
  countryDataJournalResponse: CountryDataJournalResponse;
  platformMetric: PlatformMetric;
  platformMetricListResponse: PlatformMetricListResponse;
  platformMetricsRecomputeSummary: PlatformMetricsRecomputeSummary;
  countryTrust: CountryTrustResponse;
  methodologySection: MethodologySection;
  methodologyList: MethodologyListResponse;
  glossaryTerm: GlossaryTerm;
  glossaryList: GlossaryListResponse;
  countryDrift: CountryDriftResponse;
  countryDriftSnapshot: CountryDriftSnapshot;
  countryDriftHistoryItem: CountryDriftHistoryItem;
  countryDriftRecomputeRequest: CountryDriftRecomputeRequest;
  countryDriftRecomputeResult: CountryDriftRecomputeResult;
  countryDriftBatchRecomputeResult: CountryDriftBatchRecomputeResult;
  searchResultItem: SearchResultItem;
  searchResponse: SearchResponse;
  aiAskRequest: AIAskRequest;
  aiAskResponse: AIAskResponse;
  aiExplainNumberRequest: AIExplainNumberRequest;
  aiExplainNumberResponse: AIExplainNumberResponse;
  aiDecisionIntentRequest: AIDecisionIntentRequest;
  aiDecisionIntentResponse: AIDecisionIntentResponse;
  aiCitation: AICitation;
  aiProviderMeta: AIProviderMeta;
  aiDraft: AIDraft;
  aiDraftListResponse: AIDraftListResponse;
  contradictionCandidate: ContradictionCandidate;
  contradictionCandidateListResponse: ContradictionCandidateListResponse;
  communityQuestion: CommunityQuestion;
  communityQuestionListResponse: CommunityQuestionListResponse;
  communityAnswer: CommunityAnswer;
  consensusSummary: ConsensusSummary;
  voteSummary: VoteSummary;
  dataErrorReport: DataErrorReport;
  userStoryRating: UserStoryRating;
  authUser: AuthUser;
  authSession: AuthSession;
  authTokenResponse: AuthTokenResponse;
  registerRequest: RegisterRequest;
  loginRequest: LoginRequest;
  currentUserResponse: CurrentUserResponse;
  userSessionListResponse: UserSessionListResponse;
  telegramLinkRequest: TelegramLinkRequest;
  telegramLinkResponse: TelegramLinkResponse;
  telegramLinkStatusResponse: TelegramLinkStatusResponse;
  watchlistItem: WatchlistItem;
  watchlistResponse: WatchlistResponse;
  watchlistStatusResponse: WatchlistStatusResponse;
  adminUser: AdminUser;
  adminUserListResponse: AdminUserListResponse;
  roleUpdateRequest: RoleUpdateRequest;
  userStatusUpdateRequest: UserStatusUpdateRequest;
  migrationBoardPostList: MigrationBoardPostListResponse;
  migrationBoardPostDetail: MigrationBoardPostDetail;
  myMigrationBoardPost: MyMigrationBoardPost;
  myMigrationBoardPostList: MyMigrationBoardPostListResponse;
  createMigrationBoardPostRequest: CreateMigrationBoardPostRequest;
  updateMigrationBoardPostRequest: UpdateMigrationBoardPostRequest;
  migrationBoardContactRequest: ContactRequestResponse;
  migrationBoardContactRequestList: ContactRequestListResponse;
  migrationBoardMatches: CompanionMatchesResponse;
  migrationBoardReport: MigrationBoardReportResponse;
  adminMigrationBoardPostList: AdminMigrationBoardPostListResponse;
};
