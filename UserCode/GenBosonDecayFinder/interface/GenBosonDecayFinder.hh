#include <vector>
#include <sstream>
#include <string>

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

using namespace reco;
using namespace std;

class GenBosonDecayFinder
{

public:
    GenBosonDecayFinder(const GenParticleCollection);
    ~GenBosonDecayFinder()


};

GenBosonDecayFinder::GenBosonDecayFinder(const GenParticleCollection genparticles)
{

  std::cout<<genparticles.size()<<endl;

}


GenBosonDecayFinder::~GenBosonDecayFinder(){}