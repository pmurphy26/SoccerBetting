import { useEffect, useRef, useState } from "react";
import { ToastContainer, ToastOptions, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import {
  TEAM_ID_TO_NAME,
  BUNDESLIGA_TEAM_ID_TO_NAME,
  LALIGA_TEAM_ID_TO_NAME,
  SERIEA_TEAM_ID_TO_NAME,
  LIGUE1_TEAM_ID_TO_NAME,
} from "./constants";
import { User, NetworkData, TimeGrouping, GRAPH_INTERFACE } from "./types";
import ProfitChart from "./BarChart";
import { CheckboxDropdown } from "./CheckBoxDropdown";
import { NetworkDataStatsTable } from "./StatsTable";
import {
  filterNetworkData,
  getMaxID,
  makePredictionFromOdds,
  scoreMatrix,
  wdlFromScoreMatrix,
} from "./helpers";
import { convertDateStrToSeason } from "./leagueDates";
import { CollapsableElem } from "./CollapsableElement";

const toastFormat = {
  position: "bottom-right",
  autoClose: 2500,
  hideProgressBar: true,
  closeOnClick: true,
  pauseOnHover: false,
  draggable: false,
  theme: "light",
} as ToastOptions;

function App() {
  const useMockUser = true; //process.env.REACT_APP_USE_MOCK_USER === "true";
  const [user, setUser] = useState<User>({} as unknown as User);

  const [allNetworkDatas, setAllNetworkDatas] = useState<NetworkData[]>([]);
  const [filteredNetworkDatas, setFilteredNetworkDatas] = useState<
    NetworkData[]
  >([]);
  const [newNetworkData, setNewNetworkData] = useState<NetworkData[]>([]);
  const [profit, setProfit] = useState<number>(0);

  const [showMatchInfo, setShowMatchInfo] = useState(true);
  const [showBookOdds, setShowBookOdds] = useState(true);
  const [showPredictedOdds, setShowPredictedOdds] = useState(true);
  const [showScores, setShowScores] = useState(true);
  const [showLabels, setShowLabels] = useState(true);

  const [filters, setFilters] = useState({
    teamID: [
      ...Object.keys(BUNDESLIGA_TEAM_ID_TO_NAME),
      ...Object.keys(LALIGA_TEAM_ID_TO_NAME),
      ...Object.keys(SERIEA_TEAM_ID_TO_NAME),
      ...Object.keys(LIGUE1_TEAM_ID_TO_NAME),
    ] as string[],
    matchStartDate: "",
    matchEndDate: "",
    minHomeOdds: "",
    minDrawOdds: "",
    minAwayOdds: "",
    matchLabel: "",
    completed: "",
    useGoodBetsOnly: true,
  });
  const [goodBetFilters, setGoodBetFilters] = useState({
    minBetOdds: 1.5,
    drawThreshold: 0.3,
    badGap: 0.25,
  });
  const [leagueFilter, setLeagueFilter] = useState<boolean[]>([
    true,
    true,
    true,
    true,
  ]);
  const LEAGUE_DICT_ARR = [
    BUNDESLIGA_TEAM_ID_TO_NAME,
    LALIGA_TEAM_ID_TO_NAME,
    SERIEA_TEAM_ID_TO_NAME,
    LIGUE1_TEAM_ID_TO_NAME,
  ];
  const [graphViewType, setGraphViewType] = useState<GRAPH_INTERFACE>(
    GRAPH_INTERFACE.showMultipleLeagues,
  );
  const DICT_ID_TO_NAME = ["BUNDESLIGA", "LA LIGA", "SERIE A", "LIGUE 1"];
  const INDEX_TO_NAME = ["home", "draw", "away"];
  const [grouping, setGrouping] = useState<TimeGrouping>("biweekly");

  function getPredictedLabelForNewData(
    newData: NetworkData[],
    oldData: NetworkData[],
    networkInputs?: number[][],
  ) {
    setNewNetworkData(
      newData.map((nd) => {
        const oldDataIndex: number = oldData.findIndex((od) => nd.id == od.id);
        if (oldDataIndex >= 0)
          return {
            ...nd,
            predicted: {
              ...oldData[oldDataIndex].predicted,
            },
          } as NetworkData;

        return { ...(nd as NetworkData) };
      }),
    );
  }

  function getResultFromLabel(label: number[]): number {
    try {
      return label[0] > label[1] ? 0 : label[0] < label[1] ? 2 : 1;
    } catch {
      return -1;
    }
  }

  async function alterSelectedNetworkData() {
    try {
      const res = await fetch("http://localhost:8000/api/matches/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          matches: filteredNetworkDatas
            .filter((fnd) => newNetworkData.some((nd) => nd.id == fnd.id))
            .map((fd) => {
              const nnd = newNetworkData.findIndex((nd) => nd.id == fd.id);
              return {
                matchDate: fd.matchInfo.matchDate,
                team1ID: newNetworkData[nnd].matchInfo.team1ID,
                team2ID: newNetworkData[nnd].matchInfo.team2ID,
                id: fd.id,
                team1IsHome: newNetworkData[nnd].matchInfo.team1IsHome,
                completed: true, //fd.matchInfo.completed,
              };
            }),
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const resResults = await fetch("http://localhost:8000/api/final_score/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          scores: filteredNetworkDatas
            .filter((fnd) => newNetworkData.some((nd) => nd.id == fnd.id))
            .map((fd) => {
              const nnd = newNetworkData.findIndex((nd) => nd.id == fd.id);
              return {
                id: fd.id,
                home_team_score: newNetworkData[nnd].finalScore?.home,
                away_team_score: newNetworkData[nnd].finalScore?.away,
                match_result: newNetworkData[nnd].finalScore?.matchResult,
              };
            }),
        }),
      });

      if (!resResults.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const resPreds = await fetch("http://localhost:8000/api/predictions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          predictions: filteredNetworkDatas
            .filter((fnd) => newNetworkData.some((nd) => nd.id == fnd.id))
            .map((fd) => {
              const nnd = newNetworkData.findIndex((nd) => nd.id == fd.id);
              return {
                id: fd.id,
                home_team_odds: newNetworkData[nnd].predicted.home,
                draw_odds: newNetworkData[nnd].predicted.draw,
                away_team_odds: newNetworkData[nnd].predicted.away,
                predicted_result: newNetworkData[nnd].predicted.predictedResult,
              };
            }),
        }),
      });

      if (!resPreds.ok) {
        throw new Error(`Server returned ${resPreds.status}`);
      }

      toast.success(`Successfully added NetworkData`, toastFormat);
      //setAllNetworkDatas([...allNetworkDatas, newNetworkData]);
    } catch (err: any) {
      if (err instanceof Error) {
        toast.error(err?.message, toastFormat);
      } else {
        toast.error(`Could not bulk create data`, toastFormat);
      }
    }
  }

  async function alterNewNetworkData() {
    try {
      const maxID = getMaxID(allNetworkDatas) + 1;
      const res = await fetch("http://localhost:8000/api/matches/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          matches: newNetworkData.map((fd, id) => {
            return {
              matchDate: fd.matchInfo.matchDate,
              team1ID: fd.matchInfo.team1ID,
              team2ID: fd.matchInfo.team2ID,
              id: maxID + id,
              team1IsHome: fd.matchInfo.team1IsHome,
              completed: false, //fd.matchInfo.completed,
            };
          }),
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const alteredData = await res.json();
      const data: NetworkData[] = [
        ...alteredData["updated"].map(
          (d: {
            id: number;
            matchDate: string;
            team1ID: number;
            team2ID: number;
            team1IsHome: boolean;
            completed: boolean;
          }) => {
            return {
              id: d.id,
              matchInfo: {
                matchDate: d.matchDate,
                team1ID: d.team1ID,
                team2ID: d.team2ID,
                team1IsHome: d.team1IsHome,
                completed: d.completed,
              },
            } as NetworkData;
          },
        ),
        alteredData["created"].map(
          (d: {
            id: number;
            matchDate: string;
            team1ID: number;
            team2ID: number;
            team1IsHome: boolean;
            completed: boolean;
          }) => {
            return {
              id: d.id,
              matchInfo: {
                matchDate: d.matchDate,
                team1ID: d.team1ID,
                team2ID: d.team2ID,
                team1IsHome: d.team1IsHome,
                completed: d.completed,
              },
            } as NetworkData;
          },
        ),
      ];

      const resResults = await fetch("http://localhost:8000/api/final_score/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          scores: newNetworkData.map((fd) => {
            return {
              id: findMatchWithKey(
                fd.matchInfo.matchDate,
                fd.matchInfo.team1ID,
                fd.matchInfo.team2ID,
                data,
              ),
              home_team_score: fd.finalScore?.home,
              away_team_score: fd.finalScore?.away,
              match_result: fd.finalScore?.matchResult,
            };
          }),
        }),
      });

      if (!resResults.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const resPreds = await fetch("http://localhost:8000/api/predictions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          predictions: newNetworkData.map((fd, id) => {
            return {
              id: findMatchWithKey(
                fd.matchInfo.matchDate,
                fd.matchInfo.team1ID,
                fd.matchInfo.team2ID,
                data,
              ),
              home_team_odds: fd.predicted.home,
              draw_odds: fd.predicted.draw,
              away_team_odds: fd.predicted.away,
              predicted_result: fd.predicted.predictedResult,
            };
          }),
        }),
      });

      if (!resPreds.ok) {
        throw new Error(`Server returned ${resPreds.status}`);
      }

      const resBookOdds = await fetch("http://localhost:8000/api/book_odds/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          odds: newNetworkData.map((fd) => {
            return {
              id: findMatchWithKey(
                fd.matchInfo.matchDate,
                fd.matchInfo.team1ID,
                fd.matchInfo.team2ID,
                data,
              ),
              home_win: fd.bookOdds?.home,
              draw: fd.bookOdds?.draw,
              away_win: fd.bookOdds?.away,
            };
          }),
        }),
      });

      if (!resBookOdds.ok) {
        throw new Error(`Server returned ${resBookOdds.status}`);
      }

      toast.success(`Successfully added NetworkData`, toastFormat);
      //setAllNetworkDatas([...allNetworkDatas, newNetworkData]);
    } catch (err: any) {
      if (err instanceof Error) {
        toast.error(err?.message, toastFormat);
      } else {
        toast.error(`Could not bulk create data`, toastFormat);
      }
    }
  }

  async function createMatchResults() {
    try {
      // Remove duplicates based on (team1ID, team2ID, matchDate)
      /*
      const uniqueMap = new Map();

      for (const item of allNetworkDatas) {
        const key = `${item.matchInfo.team1ID}-${item.matchInfo.team2ID}-${item.matchInfo.matchDate}`;
        if (!uniqueMap.has(key)) {
          uniqueMap.set(key, item);
        }
      }

      const uniqueDatas = Array.from(uniqueMap.values()).map((c) => c.id);

      const res = await fetch("http://localhost:8000/api/final_score/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          scores: uniqueDatas.map((id) => ({
            id: id,
            home_team_score: matchResults[id][0],
            away_team_score: matchResults[id][1],
            match_result: getResultFromLabel(matchResults[id]),
          })),
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      toast.success(`Successfully added Final Scores`, toastFormat);
      */
      //setAllNetworkDatas([...allNetworkDatas, newNetworkData]);
    } catch (err: any) {
      if (err instanceof Error) {
        toast.error(err?.message, toastFormat);
      } else {
        toast.error(`Could not bulk create data`, toastFormat);
      }
    }
  }

  async function createPredictionResults() {
    try {
      // Remove duplicates based on (team1ID, team2ID, matchDate)
      /*
      const uniqueMap = new Map();

      for (const item of allNetworkDatas) {
        const key = `${item.matchInfo.team1ID}-${item.matchInfo.team2ID}-${item.matchInfo.matchDate}`;
        if (!uniqueMap.has(key)) {
          uniqueMap.set(key, item);
        }
      }

      const uniqueDatas = Array.from(uniqueMap.values()).map((c) => c.id);

      const res = await fetch("http://localhost:8000/api/predictions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          predictions: uniqueDatas.map((id) => ({
            id: id,
            home_team_odds: predictedOdds[id][0],
            draw_odds: predictedOdds[id][1],
            away_team_odds: predictedOdds[id][1],
            predicted_result: matchPredictionsFromOdds[id],
          })),
        }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }
      */
      toast.success(`Successfully added Final Scores`, toastFormat);
      //setAllNetworkDatas([...allNetworkDatas, newNetworkData]);
    } catch (err: any) {
      if (err instanceof Error) {
        toast.error(err?.message, toastFormat);
      } else {
        toast.error(`Could not bulk create data`, toastFormat);
      }
    }
  }

  function findMatchWithKey(
    dateStr: string,
    team1ID: number,
    team2ID: number,
    dataToSearch: NetworkData[] = allNetworkDatas,
  ) {
    //console.log(dateStr);
    //console.log(team1ID);
    //console.log(team2ID);
    return (
      dataToSearch[
        dataToSearch.findIndex(
          (d) =>
            d.matchInfo.matchDate === dateStr &&
            ((d.matchInfo.team1ID === team1ID &&
              d.matchInfo.team2ID === team2ID) ||
              (d.matchInfo.team2ID === team1ID &&
                d.matchInfo.team1ID === team2ID)),
        )
      ]?.id ?? -1
    );
  }

  async function makePrediction(predictedData: NetworkData[]) {
    let homeFormInput: number[][] = [];
    let awayFormInput: number[][] = [];
    let homeStrengthInput: number[][] = [];
    let awayStrengthInput: number[][] = [];
    predictedData.map((nnd) => {
      homeFormInput.push(nnd.networkInput?.home_form ?? [-1]);
      awayFormInput.push(nnd.networkInput?.away_form ?? [-1]);
      homeStrengthInput.push(nnd.networkInput?.home_strength ?? [-1]);
      awayStrengthInput.push(nnd.networkInput?.away_strength ?? [-1]);
    });

    const res = await fetch("http://localhost:8000/api/predict/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        inputs: [
          homeFormInput,
          awayFormInput,
          homeStrengthInput,
          awayStrengthInput,
        ],
      }),
    });

    if (!res.ok) {
      throw new Error(`Failed to fetch NetworkDatas: ${res.status}`);
    }

    const data = await res.json();
    //console.log(data.predictions.length, predictedData.length);

    setNewNetworkData(
      predictedData.map((p: NetworkData, id: number) => {
        const pred = data.predictions[id];
        if (!pred) {
          return p;
        }
        const { homeWin, draw, awayWin } = wdlFromScoreMatrix(
          scoreMatrix(data.predictions[id][0], data.predictions[id][1]),
        );
        return {
          ...p,
          predicted: {
            home: homeWin,
            draw: draw,
            away: awayWin,
            predictedResult: makePredictionFromOdds({ homeWin, draw, awayWin }),
          },
        } as NetworkData;
      }),
    );

    //actually save to db now
  }

  async function getThisYearNetworkDatas() {
    const res = await fetch("http://localhost:8000/api/network_data/");

    if (!res.ok) {
      throw new Error(`Failed to fetch NetworkDatas: ${res.status}`);
    }

    const data = await res.json();
    //console.log(data);
    getPredictedLabelForNewData(
      data["network_data"].map((d: string[], idx: number) => {
        const adj = d[9] == "True" ? 0 : 1;
        const team1ID = Number(d[7 + adj]);
        const team2ID = Number(d[8 - adj]);
        const dateStr = d[6].split("T")[0];
        const matchID = findMatchWithKey(dateStr, team1ID, team2ID);
        return {
          id: matchID,
          matchInfo: {
            matchDate: dateStr,
            team1ID: team1ID,
            team2ID: team2ID,
            team1IsHome: d[9] == "True",
          },
          bookOdds: {
            home: Number(d[3]),
            draw: Number(d[4]),
            away: Number(d[5]),
          },
          predicted: {},
          finalScore: {
            home: Number(d[10 + adj]),
            away: Number(d[11 - adj]),
            matchResult:
              Number(d[10 + adj]) > Number(d[11 - adj])
                ? 0
                : Number(d[10 + adj]) < Number(d[11 - adj])
                  ? 2
                  : 1,
          },
          networkInput: {
            home_strength: data["network_inputs"][0][idx],
            away_strength: data["network_inputs"][1][idx],
            home_form: data["network_inputs"][2][idx],
            away_form: data["network_inputs"][3][idx],
          },
        } as NetworkData;
      }),
      filteredNetworkDatas,
      data["network_inputs"],
    );
  }

  async function getAllNetworkDatas() {
    const res = await fetch("http://localhost:8000/api/matches/");

    if (!res.ok) {
      throw new Error(`Failed to fetch NetworkDatas: ${res.status}`);
    }

    const data = await res.json();
    //console.log(data);

    // data["network_data"] is an array of rows
    const nnd = data
      .filter((d: any) => "predicted" in d)
      .map((d: NetworkData) => {
        return { ...d };
      });
    setAllNetworkDatas(nnd);
  }

  // async wrapper for fetching NetworkDatas
  const loadNetworkDatas = async () => {
    try {
      await getAllNetworkDatas();
      //setAllNetworkDatas(NetworkDatas);
    } catch (err) {
      toast.error(`Failed to load NetworkDatas:${err}`, toastFormat);
      setAllNetworkDatas([]);
    }
  };

  useEffect(() => {
    // load user
    if (useMockUser) {
      setUser({ name: "Admin" });
    } else {
      setUser({ name: "User Name" });
    }
    loadNetworkDatas();
  }, [useMockUser]);

  useEffect(() => {
    const di: Record<string, string> = {};
    leagueFilter.forEach((b, i) => {
      if (b && LEAGUE_DICT_ARR[i]) {
        Object.assign(di, LEAGUE_DICT_ARR[i]);
      }
    });
    //console.log(allNetworkDatas);
    const { data: fnd, profit: newProfit } = filterNetworkData(
      allNetworkDatas,
      0,
      di,
      filters,
      goodBetFilters,
    );
    const { data: nnd } = filterNetworkData(
      newNetworkData,
      0,
      di,
      filters,
      goodBetFilters,
    );

    //console.log(fnd.length);
    //console.log(nnd.length);
    setFilteredNetworkDatas(fnd);
    setNewNetworkData(nnd);
    //newProfit.toFixed(4);
    setProfit(newProfit);
  }, [allNetworkDatas, filters, leagueFilter, goodBetFilters]);

  const FilterUI = () => {
    return (
      <div
        style={{
          display: "flex",
          width: "100%",
          gap: "12px",
          border: "2px solid black",
          //padding: "8px",
          marginBottom: "16px",
          boxSizing: "border-box",
          backgroundColor: "#f4f4f4",
        }}
      >
        {/* Green Box */}
        <div
          style={{
            width: "35%",
            //border: "2px solid green",
            padding: "8px",
            boxSizing: "border-box",
          }}
        >
          <CheckboxDropdown
            label="Bundesliga"
            options={Object.entries(BUNDESLIGA_TEAM_ID_TO_NAME).map(
              ([id, name]) => ({
                id: Number(id),
                name,
              }),
            )}
            selected={filters.teamID.map((elem) => Number(elem))}
            onChange={(e) => {
              if (e.length != 0) {
                setFilters({
                  ...filters,
                  teamID: e.map((elem) => String(elem)),
                });
              } else {
                setFilters({
                  ...filters,
                  teamID: filters.teamID.filter(
                    (t_id) => !(t_id in BUNDESLIGA_TEAM_ID_TO_NAME),
                  ),
                });
              }
            }}
          />
          <CheckboxDropdown
            label="LaLiga"
            options={Object.entries(LALIGA_TEAM_ID_TO_NAME).map(
              ([id, name]) => ({
                id: Number(id),
                name,
              }),
            )}
            selected={filters.teamID.map((elem) => Number(elem))}
            onChange={(e) => {
              if (e.length != 0) {
                setFilters({
                  ...filters,
                  teamID: e.map((elem) => String(elem)),
                });
              } else {
                setFilters({
                  ...filters,
                  teamID: filters.teamID.filter(
                    (t_id) => !(t_id in LALIGA_TEAM_ID_TO_NAME),
                  ),
                });
              }
            }}
          />
          <CheckboxDropdown
            label="SerieA"
            options={Object.entries(SERIEA_TEAM_ID_TO_NAME).map(
              ([id, name]) => ({
                id: Number(id),
                name,
              }),
            )}
            selected={filters.teamID.map((elem) => Number(elem))}
            onChange={(e) => {
              if (e.length != 0) {
                setFilters({
                  ...filters,
                  teamID: e.map((elem) => String(elem)),
                });
              } else {
                setFilters({
                  ...filters,
                  teamID: filters.teamID.filter(
                    (t_id) => !(t_id in SERIEA_TEAM_ID_TO_NAME),
                  ),
                });
              }
            }}
          />
          <CheckboxDropdown
            label="Ligue1"
            options={Object.entries(LIGUE1_TEAM_ID_TO_NAME).map(
              ([id, name]) => ({
                id: Number(id),
                name,
              }),
            )}
            selected={filters.teamID.map((elem) => Number(elem))}
            onChange={(e) => {
              if (e.length != 0) {
                setFilters({
                  ...filters,
                  teamID: e.map((elem) => String(elem)),
                });
              } else {
                setFilters({
                  ...filters,
                  teamID: filters.teamID.filter(
                    (t_id) => !(t_id in LIGUE1_TEAM_ID_TO_NAME),
                  ),
                });
              }
            }}
          />
        </div>

        {/* Red Box */}
        <div
          style={{
            flex: 1,
            //border: "2px solid red",
            //padding: "8px",
            boxSizing: "border-box",
          }}
        >
          <div
            style={{
              display: "flex",
              flexDirection: "row",
              //gap: "8px",
              overflowX: "auto",
              //padding: "8px",
              width: "100%",
              height: "100%",
              alignItems: "stretch",
              justifyContent: "flex-end",
            }}
          >
            {/* DATE + LABEL FILTERS */}
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "12px",
                paddingRight: "8px",
              }}
            >
              <label>
                Start Date:
                <input
                  type="date"
                  value={filters.matchStartDate}
                  onChange={(e) =>
                    setFilters({
                      ...filters,
                      matchStartDate: e.target.value || "",
                    })
                  }
                />
              </label>

              <label>
                End Date:
                <input
                  type="date"
                  value={filters.matchEndDate}
                  onChange={(e) =>
                    setFilters({
                      ...filters,
                      matchEndDate: e.target.value || "",
                    })
                  }
                />
              </label>

              <label>
                Match Label:
                <select
                  value={filters.matchLabel}
                  onChange={(e) =>
                    setFilters({ ...filters, matchLabel: e.target.value })
                  }
                >
                  <option value="">All</option>
                  <option value="0">Home Win</option>
                  <option value="1">Draw</option>
                  <option value="2">Away Win</option>
                </select>
              </label>
            </div>
            <CollapsableElem
              title={"Good Bet Threshold"}
              expandedSize={45}
              expandHorizontally={true}
            >
              {/* MIN PREDICTED ODDS */}
              <div
                style={{
                  display: "flex",
                  //flexDirection: "column",
                  gap: "12px",
                }}
              >
                <label>
                  Min Bet odds
                  <input
                    type="number"
                    value={goodBetFilters.minBetOdds}
                    style={{
                      height: "24px",
                      width: "48px",
                      padding: "2px 6px",
                      fontSize: "12px",
                    }}
                    onChange={(e) =>
                      setGoodBetFilters({
                        ...goodBetFilters,
                        minBetOdds: Number(e.target.value),
                      })
                    }
                  />
                </label>

                <label>
                  Bad Draw Threshold:
                  <input
                    type="number"
                    style={{
                      height: "24px",
                      width: "64px",
                      padding: "2px 6px",
                      fontSize: "12px",
                    }}
                    value={goodBetFilters.drawThreshold}
                    onChange={(e) =>
                      setGoodBetFilters({
                        ...goodBetFilters,
                        drawThreshold: Number(e.target.value),
                      })
                    }
                  />
                </label>

                <label>
                  Bad Gap:
                  <input
                    type="number"
                    value={goodBetFilters.badGap}
                    style={{
                      height: "24px",
                      width: "48px",
                      padding: "2px 6px",
                      fontSize: "12px",
                    }}
                    onChange={(e) =>
                      setGoodBetFilters({
                        ...goodBetFilters,
                        badGap: Number(e.target.value),
                      })
                    }
                  />
                </label>

                <label
                  style={{ display: "flex", alignItems: "center", gap: "6px" }}
                >
                  <input
                    type="checkbox"
                    checked={filters.useGoodBetsOnly}
                    onChange={() =>
                      setFilters({
                        ...filters,
                        useGoodBetsOnly: !filters.useGoodBetsOnly,
                      })
                    }
                  />
                  {"Use only good bets"}
                </label>
              </div>
            </CollapsableElem>
            <CollapsableElem
              title={"Edit Table Columns"}
              expandedSize={30}
              expandHorizontally={true}
            >
              <div
                style={{
                  width: "100%",
                  marginTop: "1em",
                  overflowY: "auto",
                  flex: 1,
                  minHeight: 0,
                }}
              >
                <div
                  style={{
                    transform: "scale(0.85)",
                    transformOrigin: "top left",

                    display: "grid",
                    gridTemplateColumns: "repeat(3, 1fr)",
                    gridTemplateRows: "repeat(2, auto)",
                    gap: "12px",
                    maxWidth: "500px",
                  }}
                >
                  <button onClick={() => setShowMatchInfo(!showMatchInfo)}>
                    {showMatchInfo ? "Hide" : "Show"} Match Info
                  </button>

                  <button onClick={() => setShowBookOdds(!showBookOdds)}>
                    {showBookOdds ? "Hide" : "Show"} Book Odds
                  </button>

                  <button
                    onClick={() => setShowPredictedOdds(!showPredictedOdds)}
                  >
                    {showPredictedOdds ? "Hide" : "Show"} Predicted Odds
                  </button>

                  <button onClick={() => setShowScores(!showScores)}>
                    {showScores ? "Hide" : "Show"} Scores
                  </button>

                  <button onClick={() => setShowLabels(!showLabels)}>
                    {showLabels ? "Hide" : "Show"} Match Labels
                  </button>
                </div>
              </div>
            </CollapsableElem>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div style={{ padding: "2vh", fontFamily: "sans-serif" }}>
      <ToastContainer />
      <h1 style={{ height: "6vh" }}>NetworkData Viewer</h1>

      {/* Filter */}
      <FilterUI />
      {/* Graph and Table UI */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          width: "100%",
          height: "200vh", //"calc(100vh - 120px)", // adjust for navbar/header
          overflow: "hidden", // IMPORTANT
          flexDirection: "column",
        }}
      >
        {/* Top Section — Table */}
        <div
          style={{
            flex: "1 1 40%",
            minWidth: "300px",
            display: "flex",
            flexDirection: "column",
            alignSelf: "stretch",
            //border: "2px solid red",
            minHeight: 0,
          }}
        >
          <div
            style={{
              flex: 1,
              minHeight: 0,
              overflowY: "auto",
              overflowX: "hidden",
            }}
          >
            <CollapsableElem
              title={"Past Predictions"}
              expandedSize={100}
              expandHorizontally={false}
            >
              <NetworkDataStatsTable
                networkDataArr={filteredNetworkDatas}
                profit={profit}
                showMatchInfo={showMatchInfo}
                showBookOdds={showBookOdds}
                showScores={showScores}
                showLabels={showLabels}
                showPredictedOdds={showPredictedOdds}
              />
            </CollapsableElem>

            <CollapsableElem
              title={"New Data"}
              expandedSize={100}
              expandHorizontally={false}
            >
              <NetworkDataStatsTable
                networkDataArr={newNetworkData}
                profit={profit}
                showMatchInfo={showMatchInfo}
                showBookOdds={showBookOdds}
                showScores={showScores}
                showLabels={showLabels}
                showPredictedOdds={showPredictedOdds}
              />
            </CollapsableElem>
          </div>
        </div>
        <h3>Graphs</h3>
        {/* Bottom Section - Graphs */}
        <div
          style={{
            flex: "1 1 50%",
            minWidth: "300px",
            display: "flex",
            flexDirection: "column",
            overflowY: "auto",
          }}
        >
          <div
            style={{ display: "flex", flexDirection: "column", gap: "12px" }}
          >
            <select
              value={graphViewType}
              onChange={(e) => {
                console.log(e.target.value as GRAPH_INTERFACE);
                setGraphViewType(e.target.value as GRAPH_INTERFACE);
              }}
            >
              {Object.entries(GRAPH_INTERFACE).map(
                ([interfaceType, interfaceStr]) => (
                  <option key={interfaceType} value={interfaceStr}>
                    {interfaceStr}
                  </option>
                ),
              )}
            </select>

            <div
              style={{
                display: "flex",
                gap: "10px",
                marginBottom: "12px",
                flexWrap: "wrap",
              }}
            >
              <p>Select graph period: </p>
              <button onClick={() => setGrouping("weekly")}>Weekly</button>
              <button onClick={() => setGrouping("biweekly")}>Bi‑Weekly</button>
              <button onClick={() => setGrouping("monthly")}>Monthly</button>
            </div>
          </div>
          <div
            style={{
              flex: 1,
              overflowY: "auto",
              minHeight: 0,
              paddingRight: "8px",
            }}
          >
            {graphViewType == GRAPH_INTERFACE.showSingleGraph && (
              <ProfitChart data={filteredNetworkDatas} grouping={grouping} />
            )}

            {graphViewType == GRAPH_INTERFACE.showMultipleYears && (
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "16px",
                }}
              >
                {[2021, 2022, 2023, 2024, 2025].map((d) => (
                  <div
                    key={d}
                    style={{
                      flex: `1 1 calc(${100 / 5}% - 16px)`,
                      minWidth: 0,
                    }}
                  >
                    <h3>{d}</h3>
                    <ProfitChart
                      data={filteredNetworkDatas.filter(
                        (fnd) =>
                          convertDateStrToSeason(fnd.matchInfo.matchDate) == d,
                      )}
                      grouping={grouping}
                    />
                  </div>
                ))}
              </div>
            )}

            {graphViewType == GRAPH_INTERFACE.showMultipleLeagues && (
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "16px",
                }}
              >
                {leagueFilter.map((d, i) =>
                  d ? (
                    <div
                      key={i}
                      style={{
                        flex: `1 1 calc(${100 / 5}% - 16px)`,
                        minWidth: 0,
                      }}
                    >
                      <h3>{DICT_ID_TO_NAME[i]}</h3>
                      <ProfitChart
                        data={filteredNetworkDatas.filter((fnd) => {
                          if (
                            !(
                              fnd.matchInfo.team1ID.toString() in
                              LEAGUE_DICT_ARR[i]
                            ) &&
                            !(
                              fnd.matchInfo.team2ID.toString() in
                              LEAGUE_DICT_ARR[i]
                            )
                          )
                            return false;

                          return true;
                        })}
                        grouping={grouping}
                      />
                    </div>
                  ) : null,
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      {/* Buttons */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "12px",
          marginBottom: "16px",
          height: "5vh",
        }}
      >
        <button onClick={getThisYearNetworkDatas}>Get 2025 data</button>
        <button onClick={alterSelectedNetworkData}>Update New Data</button>
        <button onClick={(e) => makePrediction(newNetworkData)}>
          Make predictions for new data
        </button>
        <button onClick={alterNewNetworkData}>
          Write new network data to database, {newNetworkData.length}
        </button>
      </div>
    </div>
  );
}

export default App;
