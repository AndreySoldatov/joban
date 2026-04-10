import security from 'eslint-plugin-security'
import noSecrets from 'eslint-plugin-no-secrets'

import baseConfig from './eslint.config.js'

const sharedConfig = Array.isArray(baseConfig) ? baseConfig : [baseConfig]

export default [
  ...sharedConfig,
  {
    files: ['src/**/*.{ts,tsx}'],
    plugins: {
      security,
      'no-secrets': noSecrets,
    },
    rules: {
      ...(security.configs?.recommended?.rules ?? {}),
      'no-secrets/no-secrets': 'error',
    },
  },
]
