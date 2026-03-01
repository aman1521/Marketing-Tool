import { create } from 'zustand';
import axios from 'axios';

interface PlatformConnection {
    platform: string;
    status: 'connected' | 'disconnected';
    lastSync: string | null;
}

interface Campaign {
    id: string;
    name: string;
    status: 'active' | 'paused';
    dailyBudget: number;
    performanceMetrics: Record<string, unknown>;
    isAutoManaged: boolean;
}

interface Post {
    id: string;
    content: string;
    status: 'draft' | 'scheduled' | 'published';
    scheduledFor: string | null;
    engagementMetrics: Record<string, unknown>;
}

interface CompanyState {
    platforms: PlatformConnection[];
    campaigns: Campaign[];
    posts: Post[];
    isLoading: boolean;
    error: string | null;
    fetchPlatforms: (companyId: string) => Promise<void>;
    fetchAssets: (companyId: string, platform: string) => Promise<void>;
    updateCampaignBudget: (companyId: string, campaignId: string, newBudget: number) => Promise<void>;
    toggleAutomation: (companyId: string, campaignId: string, isAuto: boolean) => Promise<void>;
    proposeStrategy: (companyId: string, riskLevel: string) => Promise<Record<string, unknown>[]>;
}

export const useCompanyStore = create<CompanyState>((set, get) => ({
    platforms: [],
    campaigns: [],
    posts: [],
    isLoading: false,
    error: null,

    fetchPlatforms: async (companyId: string) => {
        set({ isLoading: true });
        try {
            // using the backend endpoint we just setup in API
            const response = await axios.get(`http://localhost:8000/api/v1/connectors/${companyId}/platforms`);
            set({ platforms: response.data, isLoading: false });
        } catch (e: unknown) {
            set({ error: e instanceof Error ? e.message : String(e), isLoading: false });
        }
    },

    fetchAssets: async (companyId: string, platform: string) => {
        set({ isLoading: true });
        try {
            // Live Backend Call -> Fetches joined Account -> Campaigns / Posts arrays
            const response = await axios.get(`http://localhost:8000/api/v1/companies/${companyId}/${platform}/assets`);

            set({
                campaigns: response.data.campaigns || [],
                posts: response.data.posts || [],
                isLoading: false
            });
        } catch (e: unknown) {
            set({ error: e instanceof Error ? e.message : String(e), isLoading: false, campaigns: [], posts: [] });
        }
    },

    updateCampaignBudget: async (companyId: string, campaignId: string, newBudget: number) => {
        // HTTP PUT to standard campaigns endpoint
        // await axios.put(`http://localhost:8000/api/v1/campaigns/${campaignId}`, { budget: newBudget });
        const { campaigns } = get();
        set({
            campaigns: campaigns.map(c => c.id === campaignId ? { ...c, dailyBudget: newBudget } : c)
        });
    },

    toggleAutomation: async (companyId: string, campaignId: string, isAuto: boolean) => {
        const { campaigns } = get();
        set({
            campaigns: campaigns.map(c => c.id === campaignId ? { ...c, isAutoManaged: isAuto } : c)
        });
    },

    proposeStrategy: async (companyId: string, riskLevel: string) => {
        // Will call the AI Safety Engine endpoint
        // const response = await axios.post(`http://localhost:8000/api/v1/automation/${companyId}/run`, { riskLevel });
        // return response.data;
        console.log("Mock strategy evaluation for", companyId, "at risk:", riskLevel);

        return [
            {
                "action_type": "budget_shift",
                "confidence_score": 0.82,
                "reasoning_text": "CPA dropping dramatically, shifting aggressive budget.",
                "proposed_changes": { "platform": "meta", "campaign_id": "1", "new_daily_budget": 200 },
                "requires_approval": true
            }
        ];
    }
}));
