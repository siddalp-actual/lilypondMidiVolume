\version "2.20.0"
timeAndKey =
  {\key g \major \time 4/4}

\include "articulate.ly"   % better midi dynamics

myReg =
#(define-scheme-function (parser location init-val init-incr)
    (number? number?)
    ;; init-val is explicitly frozen in the local let environment
    (let ((regVal init-val)   ;; initial value
          (regIncr init-incr)  ;; and an increment
        )
        (define (get-val)
            regVal)  ;; return the current value
        (define (set-val amount)
            (set! regVal (range-limit amount))
            regVal)  ;; return the set value
        (define (set-incr new-incr)
            (set! regIncr new-incr)
            regIncr)  ;; return the set value
        (define (up-val)
            (set! regVal (range-limit (* regIncr (get-val))))
            regVal)  ;; return the new value
        (define (range-limit val)
            ;; limit val to [0, 1]
            (cond
                ((> val 1) 1.0)
                ((< val 0) 0.0)
                (#t val)
             )
        )

        ;; think of this as constructor which binds the methods to the state
        (lambda args
            (apply
                (case (car args)
                    ;; get-value is frozen as its value in the lambda
                    ((get-value) get-val)
                    ((set-value) set-val)
                    ((up-value) up-val)
                    (else (error "Invalid method!")))
                (cdr args)
            )
        )
    )
)

spf = #(make-dynamic-script "spf")
rpf = #(make-dynamic-script "rpf")

% define the volume register to use myReg function with
% initial values of 0.5 for volume and an increment multiplier
% of 1.1x the current volume
% volume ranges from 0 to 1 corresponding to midi velocity 0-127
#(define volume (myReg 0.5 1.1))  % 0.5 * 127 = 63

#(define (myDynamics dynamic)
    (cond
        ((equal? dynamic "spf")  (volume 'up-value))
        ((equal? dynamic "rpf")  (volume 'get-value))
        (#t (default-dynamic-absolute-volume dynamic))
    )
)


pianoupper = \relative c'' {
    \tempo 4 = 120
    \set Score.dynamicAbsoluteVolumeFunction = #myDynamics


    \clef treble
    \timeAndKey
    <<
        \new Voice {
            \voiceOne
            \set midiPanPosition = -0.75

            \repeat volta 6 {
                c4\spf b4 a4 g4
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
            \set midiPanPosition = 0.75
            <<
            \repeat volta 6 {
                c4\rpf\sustainOn d4 e4\sustainOff f4
            }
            >>
        }
    >>
}

pianostaff =
    \new PianoStaff
    <<
        \set PianoStaff.instrumentName = "Piano"
        %\staffName "Piano"
        \new Staff = "up" \pianoupper
        % although this method of separating dynamics leads to
        % elegant print, it doesn't seem to effect the midi
        \new Dynamics = "expression"{s4\p s4\mf s4\ff s4}
        \new Staff = "down" \pianolower
        \new Dynamics = "pedal" {
            s4\sustainOn s2 s4\sustainOff
        }
    >>

\score {
    \unfoldRepeats
    \pianostaff
    \layout {

    }
    \midi {
        \context {
          \Score
         % midiMinimumVolume = #0.8
      }
        \context {
           \PianoStaff
           \accepts Dynamics
         }
    }
}

%{
\displayMusic{            \repeat volta 2 {
                c4\cr d4 e4\ff f4
            }
}
%}
