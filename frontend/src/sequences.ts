import * as Icon from "react-bootstrap-icons";

interface Sequence {
  name: string;
  endpoint: string;
  icon?: Icon.Icon;
  variant?: string;
}

export const sequences: Sequence[] = [
  {
    name: "Chromecast",
    endpoint: "chromecast",
    icon: Icon.Tv,
  },
  {
    name: "Cubert",
    endpoint: "cubert",
    icon: Icon.Cpu,
  },
  {
    name: "Switch",
    endpoint: "switch",
    icon: Icon.Controller,
  },
  {
    name: "Vinyl",
    endpoint: "vinyl",
    icon: Icon.Vinyl,
  },
  {
    name: "AirPlay",
    endpoint: "airplay",
    icon: Icon.Cast,
  },
  {
    name: "I'm done",
    endpoint: "all_off",
    icon: Icon.Power,
    variant: "outline-danger",
  },
];
