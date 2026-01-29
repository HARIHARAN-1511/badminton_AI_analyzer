const getApiUrls = () => {
    const isProd = process.env.NODE_ENV === 'production';
    // Replace the placeholder below with your Hugging Face space URL after you create it
    const prodUrl = 'https://goku2025-badminton-analysis.hf.space';
    const localUrl = 'http://localhost:8000';

    const baseUrl = isProd ? prodUrl : localUrl;

    return {
        API_BASE_URL: baseUrl,
        WS_BASE_URL: baseUrl.replace('http', 'ws'),
    };
};

export const { API_BASE_URL, WS_BASE_URL } = getApiUrls();
