import type { ModelProviderType } from '@/types/model';

declare module '@/types/model' {
  interface ModelFilterParams {
    provider?: ModelProviderType | string;
  }

  interface ModelFormData {
    provider?: ModelProviderType | string;
  }

  interface ModelCreateParams {
    provider?: ModelProviderType | string;
  }
}
