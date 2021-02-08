\version "2.20.0"
timeAndKey =
  {\key g \major \time 4/4}



pianoupper = \relative c'' {
    \tempo 4 = 120

    \clef treble
    \timeAndKey
    <<
        \new Voice {
            \voiceOne
            \repeat volta 2 {
                c4 b4 a4 g4
            }
        }
    >>
}

pianolower = \relative c {
    \clef bass
    \timeAndKey
    <<
        \new Voice {
            \voiceTwo
            \repeat volta 2 {
                c4 d4 e4 f4
            }
        }
    >>
}

pianostaff =
    <<
        \set PianoStaff.instrumentName = "Piano"
        %\staffName "Piano"
        \new Staff = "up" \pianoupper
        \new Staff = "down" \pianolower
    >>

\score {
    \pianostaff
    \layout {

    }
    \midi {
        \context {
          \Score
          %midiMinimumVolume = #0.8
      }
    }
}
