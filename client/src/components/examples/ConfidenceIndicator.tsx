import ConfidenceIndicator from '../ConfidenceIndicator';

export default function ConfidenceIndicatorExample() {
  return (
    <div className="p-6 space-y-6 max-w-sm">
      <div>
        <h3 className="text-sm font-medium mb-3">High Confidence (85%)</h3>
        <ConfidenceIndicator score={85} />
      </div>
      
      <div>
        <h3 className="text-sm font-medium mb-3">Medium Confidence (65%)</h3>
        <ConfidenceIndicator score={65} />
      </div>
      
      <div>
        <h3 className="text-sm font-medium mb-3">Low Confidence (45%)</h3>
        <ConfidenceIndicator score={45} />
      </div>
      
      <div>
        <h3 className="text-sm font-medium mb-3">Compact Version</h3>
        <ConfidenceIndicator score={75} size="sm" showIcon={false} />
      </div>
    </div>
  );
}