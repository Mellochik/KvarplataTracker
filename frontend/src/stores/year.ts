import { ref } from 'vue'

const selectedYear = ref(new Date().getFullYear())

export function useYearStore() {
  return { selectedYear }
}