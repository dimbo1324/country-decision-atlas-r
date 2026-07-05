import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { generateDataset, type Dataset } from "@/data/generator";

interface DatasetContextValue {
  dataset: Dataset;
  isRunning: boolean;
  runAnalysis: () => void;
}

const DatasetContext = createContext<DatasetContextValue | null>(null);

const ANALYSIS_DURATION_MS = 1600;

export function DatasetProvider({ children }: { children: ReactNode }) {
  const [dataset, setDataset] = useState<Dataset>(() => generateDataset());
  const [isRunning, setIsRunning] = useState(false);

  const runAnalysis = useCallback(() => {
    setIsRunning((current) => {
      if (current) return current;
      window.setTimeout(() => {
        setDataset(generateDataset());
        setIsRunning(false);
      }, ANALYSIS_DURATION_MS);
      return true;
    });
  }, []);

  const value = useMemo(
    () => ({ dataset, isRunning, runAnalysis }),
    [dataset, isRunning, runAnalysis],
  );

  return (
    <DatasetContext.Provider value={value}>{children}</DatasetContext.Provider>
  );
}

export function useDataset(): DatasetContextValue {
  const context = useContext(DatasetContext);
  if (!context) {
    throw new Error("useDataset must be used within a DatasetProvider");
  }
  return context;
}
