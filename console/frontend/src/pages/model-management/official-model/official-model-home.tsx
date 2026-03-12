import React, { useMemo, useState } from 'react';
import { Button } from 'antd';
import { useTranslation } from 'react-i18next';
import ModelManagementHeader from '../components/model-management-header';
import CategoryAside from '../components/category-aside';
import { CreateModal } from '../components/modal-component';
import { ModelProvider, useModelContext } from '../context/model-context';
import { useModelFilters } from '../hooks/use-model-filters';
import { ModelProviderType } from '@/types/model';
import { getModelProviderLabel } from '../utils/provider';

interface OfficialProviderCard {
  provider: ModelProviderType;
  title: string;
  subtitle: string;
  description: string;
  accentClass: string;
}

const OfficialModelContent: React.FC = () => {
  const { t } = useTranslation();
  const { state, actions } = useModelContext();
  const filters = useModelFilters();
  const [selectedProvider, setSelectedProvider] =
    useState<ModelProviderType | null>(null);

  const providerCards = useMemo<OfficialProviderCard[]>(
    () => [
      {
        provider: ModelProviderType.ANTHROPIC,
        title: 'Claude',
        subtitle: 'Sonnet / Opus',
        description: t('model.providerCardAnthropicDesc'),
        accentClass: 'from-[#FDF3E8] via-[#FFF8F2] to-white',
      },
      {
        provider: ModelProviderType.GOOGLE,
        title: 'Gemini',
        subtitle: '2.5 Flash / 2.5 Pro',
        description: t('model.providerCardGoogleDesc'),
        accentClass: 'from-[#EAF4FF] via-[#F5F9FF] to-white',
      },
      {
        provider: ModelProviderType.DEEPSEEK,
        title: 'DeepSeek',
        subtitle: 'V3 / R1',
        description: t('model.providerCardDeepSeekDesc'),
        accentClass: 'from-[#EEF2FF] via-[#F7F8FF] to-white',
      },
    ],
    [t]
  );

  const visibleCards = useMemo(() => {
    const keyword = state.searchInput.trim().toLowerCase();

    return providerCards.filter(card => {
      const matchedProvider =
        !state.providerFilter || state.providerFilter === card.provider;
      const matchedKeyword =
        !keyword ||
        card.title.toLowerCase().includes(keyword) ||
        card.subtitle.toLowerCase().includes(keyword) ||
        card.description.toLowerCase().includes(keyword) ||
        getModelProviderLabel(card.provider).toLowerCase().includes(keyword);

      return matchedProvider && matchedKeyword;
    });
  }, [providerCards, state.providerFilter, state.searchInput]);

  const handleOpenProviderModal = (provider: ModelProviderType): void => {
    actions.setCurrentEditModel(undefined);
    setSelectedProvider(provider);
  };

  return (
    <div className="w-full h-screen flex flex-col page-container-inner-UI">
      <div className="flex-none mb-5">
        <ModelManagementHeader
          activeTab="officialModel"
          shelfOffModel={[]}
          searchInput={state.searchInput}
          setSearchInput={filters.handleSearchInputChange}
          setShowShelfOnly={() => undefined}
        />
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="mx-auto h-full w-full flex gap-6 lg:gap-2">
          <aside className="w-full lg:w-[224px] max-w-[224px] min-w-[180px] flex-shrink-0 rounded-[18px] bg-[#FFFFFF] overflow-y-auto hide-scrollbar shadow-sm">
            <CategoryAside
              tree={[]}
              providerFilter={state.providerFilter}
              providerOptions={[
                {
                  label: t('model.providerDeepSeek'),
                  value: ModelProviderType.DEEPSEEK,
                },
                {
                  label: t('model.providerAnthropic'),
                  value: ModelProviderType.ANTHROPIC,
                },
                {
                  label: t('model.providerGoogle'),
                  value: ModelProviderType.GOOGLE,
                },
              ]}
              onProviderChange={filters.handleProviderFilterChange}
              showContextLength={false}
            />
          </aside>

          <main className="flex-1 rounded-lg overflow-y-auto [&::-webkit-scrollbar-thumb]:rounded-full">
            <div className="rounded-[24px] bg-white min-h-full p-6 shadow-sm">
              <div className="mb-6">
                <h2 className="text-[18px] font-semibold text-[#222529] leading-7">
                  {t('model.officialProviderIntro')}
                </h2>
                <p className="mt-2 text-sm text-[#7D8493] leading-6">
                  选择供应商后，填写对应模型名称、接口地址、API 密钥和参数配置。
                </p>
              </div>

              {visibleCards.length > 0 ? (
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-5">
                  {visibleCards.map(card => (
                    <section
                      key={card.provider}
                      className={`relative overflow-hidden rounded-[24px] border border-[#E8EBF4] bg-gradient-to-br ${card.accentClass} p-6 shadow-[0_10px_30px_rgba(31,35,41,0.05)]`}
                    >
                      <div className="absolute right-0 top-0 h-28 w-28 rounded-full bg-white/50 blur-2xl" />
                      <div className="relative flex h-full flex-col">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="inline-flex items-center rounded-full bg-white/80 px-3 py-1 text-xs font-medium text-[#6356EA]">
                              {getModelProviderLabel(card.provider)}
                            </div>
                            <h3 className="mt-4 text-[28px] leading-9 font-semibold text-[#1F2329]">
                              {card.title}
                            </h3>
                            <p className="mt-2 text-sm text-[#5C6475]">
                              {card.subtitle}
                            </p>
                          </div>
                          <div className="rounded-2xl border border-white/80 bg-white/70 px-4 py-3 text-right">
                            <div className="text-xs text-[#7D8493]">
                              {t('model.providerLabel')}
                            </div>
                            <div className="mt-1 text-sm font-medium text-[#222529]">
                              {getModelProviderLabel(card.provider)}
                            </div>
                          </div>
                        </div>

                        <p className="relative mt-6 flex-1 text-sm leading-6 text-[#4F566B]">
                          {card.description}
                        </p>

                        <div className="mt-6 flex items-center justify-between gap-3">
                          <div className="text-xs text-[#7D8493]">
                            支持填写自定义 URL、密钥、模型名和参数项
                          </div>
                          <Button
                            type="primary"
                            className="px-5"
                            onClick={() => handleOpenProviderModal(card.provider)}
                          >
                            {t('model.configureProvider')}
                          </Button>
                        </div>
                      </div>
                    </section>
                  ))}
                </div>
              ) : (
                <div className="flex h-[320px] items-center justify-center rounded-[24px] border border-dashed border-[#DCE2F0] bg-[#FAFBFF] text-sm text-[#7D8493]">
                  未找到匹配的官方供应商，请调整搜索词或左侧筛选条件。
                </div>
              )}
            </div>
          </main>
        </div>
      </div>

      {selectedProvider && (
        <CreateModal
          setCreateModal={() => setSelectedProvider(null)}
          initialProvider={selectedProvider}
          lockProvider={true}
          hideLocalModel={true}
          showCategoryForm={false}
        />
      )}
    </div>
  );
};

function OfficialModel(): React.JSX.Element {
  return (
    <ModelProvider>
      <OfficialModelContent />
    </ModelProvider>
  );
}

export default OfficialModel;
