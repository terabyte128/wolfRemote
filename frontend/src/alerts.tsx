import { Alert } from "react-bootstrap";

export default function LoadingMessage({ name, error }: { name: string, error: boolean }) {
    if (error) {
        return <Alert className="mt-3" variant="warning">Failed to load data from {name}.</Alert>;
    } else {
        return <Alert className="mt-3" variant="primary">Loading {name}...</Alert>;
    }
}