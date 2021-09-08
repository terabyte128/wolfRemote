import { Alert, Button } from "react-bootstrap";
import { ArrowCounterclockwise } from "react-bootstrap-icons";

export default function LoadingMessage({
    name,
    useCustomMessage,
    error,
    refreshParams,
}: {
    name: string;
    useCustomMessage?: boolean;
    error: boolean;
    refreshParams?: {
        isValidating: boolean;
        mutate: () => void;
    };
}) {
    if (error) {
        return (
            <Alert className="mt-3" variant="warning">
                {useCustomMessage ? (
                    <p>{name}</p>
                ) : (
                    <p>Failed to load data from {name}.</p>
                )}
                {refreshParams && (
                    <Button
                        variant="warning"
                        disabled={refreshParams.isValidating}
                        onClick={() => refreshParams.mutate()}
                    >
                        {refreshParams.isValidating ? (
                            "Trying again..."
                        ) : (
                            <>
                                <ArrowCounterclockwise /> Try again
                            </>
                        )}
                    </Button>
                )}
            </Alert>
        );
    } else {
        return (
            <Alert className="mt-3" variant="primary">
                Loading{!useCustomMessage && ` ${name}`}...
            </Alert>
        );
    }
}
