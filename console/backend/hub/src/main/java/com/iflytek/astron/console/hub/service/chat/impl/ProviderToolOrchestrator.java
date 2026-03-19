package com.iflytek.astron.console.hub.service.chat.impl;

import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import com.iflytek.astron.console.commons.dto.llm.SparkChatRequest;
import org.apache.commons.lang3.StringUtils;

import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Shared tool orchestration for bot debug and formal chat.
 *
 * Current provider capability matrix for enabled web search:
 * - spark: native support via SparkChatRequest.enableWebSearch
 * - google: native support via Gemini tools.google_search
 * - anthropic: native support via Anthropic web_search tool + beta header
 * - other providers: platform-managed web search, injected as external context
 */
final class ProviderToolOrchestrator {

    static final String TOOL_IFLY_SEARCH = "ifly_search";
    static final String PROVIDER_SPARK = "spark";
    static final String PROVIDER_GOOGLE = "google";
    static final String PROVIDER_ANTHROPIC = "anthropic";
    private static final String MANAGED_WEB_SEARCH_PROMPT = """
            System notice: the platform has executed a managed real-time web search for the latest user request.
            Treat the returned search context as trusted external evidence and use it when producing the final answer.
            Keep source reference indices like [1] when they appear in the provided search summary.
            """;
    private static final String SEARCH_UNAVAILABLE_NOTICE =
            "System notice: the platform could not complete the enabled real-time web search for this request. " +
                    "You must explicitly tell the user that real-time web search was unavailable and no live web search result was used.";

    private ProviderToolOrchestrator() {
    }

    static ToolExecutionPlan resolve(String provider, String openedTool) {
        Set<String> enabledTools = parseEnabledTools(openedTool);
        boolean webSearchEnabled = enabledTools.contains(TOOL_IFLY_SEARCH);
        String normalizedProvider = normalizeProvider(provider);

        if (!webSearchEnabled) {
            return new ToolExecutionPlan(normalizedProvider, enabledTools, WebSearchMode.DISABLED);
        }

        return switch (normalizedProvider) {
            case PROVIDER_SPARK -> new ToolExecutionPlan(normalizedProvider, enabledTools, WebSearchMode.SPARK_NATIVE);
            case PROVIDER_GOOGLE -> new ToolExecutionPlan(normalizedProvider, enabledTools, WebSearchMode.GOOGLE_NATIVE);
            case PROVIDER_ANTHROPIC -> new ToolExecutionPlan(normalizedProvider, enabledTools, WebSearchMode.ANTHROPIC_NATIVE);
            default -> new ToolExecutionPlan(normalizedProvider, enabledTools, WebSearchMode.PLATFORM_MANAGED);
        };
    }

    static void applyToSparkRequest(SparkChatRequest request, ToolExecutionPlan plan) {
        request.setEnableWebSearch(plan.webSearchMode() == WebSearchMode.SPARK_NATIVE);
    }

    static void applyToPromptRequest(JSONObject request, ToolExecutionPlan plan) {
        switch (plan.webSearchMode()) {
            case DISABLED -> {
                return;
            }
            case GOOGLE_NATIVE -> request.put("tools", buildGoogleTools());
            case ANTHROPIC_NATIVE -> {
                request.put("tools", buildAnthropicTools());
                request.put("anthropicBeta", "web-search-2025-03-05");
            }
            case PLATFORM_MANAGED -> request.put("managedWebSearch", true);
            case MANAGED_UNAVAILABLE -> prependSystemNotice(request, SEARCH_UNAVAILABLE_NOTICE);
            case SPARK_NATIVE -> {
                // Spark should not enter PromptChatService, but keep behavior explicit.
                prependSystemNotice(request, SEARCH_UNAVAILABLE_NOTICE);
            }
            default -> {
            }
        }
    }

    static void applyManagedSearchContext(JSONObject request, String searchSummary) {
        if (StringUtils.isBlank(searchSummary)) {
            return;
        }
        prependSystemNotice(request, MANAGED_WEB_SEARCH_PROMPT + "\n\nManaged search summary:\n" + searchSummary);
    }

    static String normalizeProvider(String provider) {
        if (StringUtils.isBlank(provider)) {
            return "openai";
        }
        return provider.trim().toLowerCase(Locale.ROOT);
    }

    private static Set<String> parseEnabledTools(String openedTool) {
        if (StringUtils.isBlank(openedTool)) {
            return Set.of();
        }
        List<String> tools = Arrays.stream(openedTool.split(","))
                .map(String::trim)
                .filter(StringUtils::isNotBlank)
                .toList();
        return new LinkedHashSet<>(tools);
    }

    private static JSONArray buildGoogleTools() {
        JSONArray tools = new JSONArray();
        tools.add(new JSONObject().fluentPut("google_search", new JSONObject()));
        return tools;
    }

    private static JSONArray buildAnthropicTools() {
        JSONArray tools = new JSONArray();
        tools.add(new JSONObject()
                .fluentPut("type", "web_search_20250305")
                .fluentPut("name", "web_search")
                .fluentPut("max_uses", 5));
        return tools;
    }

    private static void prependSystemNotice(JSONObject request, String notice) {
        JSONArray messages = request.getJSONArray("messages");
        if (messages == null) {
            messages = new JSONArray();
            request.put("messages", messages);
        }
        JSONObject systemMessage = new JSONObject();
        systemMessage.put("role", "system");
        systemMessage.put("content", notice);
        messages.add(0, systemMessage);
    }

    record ToolExecutionPlan(String provider, Set<String> enabledTools, WebSearchMode webSearchMode) {
    }

    enum WebSearchMode {
        DISABLED,
        SPARK_NATIVE,
        GOOGLE_NATIVE,
        ANTHROPIC_NATIVE,
        PLATFORM_MANAGED,
        MANAGED_UNAVAILABLE
    }
}
