import tsParser from '@typescript-eslint/parser';
import figmaPlugins from '@figma/eslint-plugin-figma-plugins';

export default [
  {
    files: ['src/**/*.ts'],
    languageOptions: {
      parser: tsParser,
      parserOptions: { project: './tsconfig.json' },
    },
    plugins: { '@figma/figma-plugins': figmaPlugins },
    rules: { ...figmaPlugins.configs.recommended.rules },
  },
];
