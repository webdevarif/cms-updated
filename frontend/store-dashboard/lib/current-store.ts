let currentStoreId: string | null = null;

export function setCurrentStoreId(id: string | null) {
  currentStoreId = id;
}

export function getCurrentStoreId() {
  return currentStoreId;
}
